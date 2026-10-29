"""Answer "Comente AGENDA" by direct message: `python -m publisher.comments --state replied.json`.

Runs every 15 minutes in the public repository (.github/workflows/comments.yml) once the app has the
instagram_business_manage_comments and instagram_business_manage_messages permissions. The state file keeps only
comment ids (the repository is public: no usernames, no comment text).
"""
import argparse
import re
import sys
import unicodedata
from datetime import timedelta
from pathlib import Path

from publisher.instagram import TOKEN_ERROR_CODE, InstagramClient, InstagramError
from shared.config import load_settings, require
from shared.jsonio import read_json, write_json
from shared.timeutil import now_local, parse_time

# Texts come from content/product.json (teste-gratis, fale-conosco, trial_url): never promise anything else here.
REPLIES = {
    "agenda": ("Oi! Como prometido: dá para testar a assistente no seu WhatsApp por 7 dias grátis, sem fidelidade e "
               "sem taxa de instalação. Comece por aqui: https://dietway.com.br/ Se quiser ver ela atendendo antes "
               "de decidir, fale com a equipe pelo WhatsApp no mesmo link."),
}
REPLY_WINDOW = timedelta(days=7)  # Instagram refuses private replies to older comments
KEEP_STATE = timedelta(days=8)


def _words(text: str) -> set[str]:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return set(re.findall(r"[a-z]+", plain))


def reply_for(text: str) -> str | None:
    words = _words(text or "")
    return next((reply for keyword, reply in REPLIES.items() if keyword in words), None)


def answer_comments(client, state: dict, now, log=print) -> int:
    """Send the keyword's reply to every new matching comment; returns how many were sent. `state` maps comment ids
    to when they were handled, and failures are recorded too, so nobody gets the same message twice."""
    sent = 0
    for media in client.recent_media():
        if now - parse_time(media["timestamp"]) > REPLY_WINDOW:
            continue
        for comment in client.comments(media["id"]):  # ponytail: first page only (50); paginate if posts get more
            reply = reply_for(comment.get("text", ""))
            own = comment.get("from", {}).get("id") == client.user_id
            if comment["id"] in state or own or not reply or now - parse_time(comment["timestamp"]) > REPLY_WINDOW:
                continue
            try:
                client.private_reply(comment["id"], reply)
                state[comment["id"]] = now.isoformat()
                sent += 1
            except InstagramError as exc:
                if exc.code == TOKEN_ERROR_CODE:
                    raise
                state[comment["id"]] = f"{now.isoformat()} failed"
                log(f"comment {comment['id']}: {exc}")
    for comment_id, handled in list(state.items()):
        if now - parse_time(handled.split()[0]) > KEEP_STATE:
            del state[comment_id]
    return sent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Answer keyword comments by direct message")
    parser.add_argument("--state", type=Path, required=True, help="JSON file with the comment ids already handled")
    args = parser.parse_args(argv)
    settings = load_settings()
    client = InstagramClient(require(settings.ig_user_id, "IG_USER_ID"),
                             require(settings.ig_access_token, "IG_ACCESS_TOKEN"))
    state = read_json(args.state) if args.state.exists() else {}
    try:
        sent = answer_comments(client, state, now_local())
    except InstagramError as exc:
        print(f"ERROR: {exc}. Token or permissions: docs/setup/accounts.md, section 6.", file=sys.stderr)
        return 1
    finally:
        write_json(args.state, state)
    print(f"{sent} direct message(s) sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
