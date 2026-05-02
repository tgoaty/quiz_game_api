# Quiz Game API

## Get started:
1. `git clone https://github.com/tgoaty/quiz_game_api`
2. `cd quiz_game_api/docker`
3. `docker compose up --build -d`
4. `cd ..`
5. `poetry install`
5. `alembic upgrade head`
6. `python3 main.py`

## Quiz sessions over WebSocket

WebSocket endpoint: `/api/session/ws`

Teacher flow:

```json
{"action":"create_session","quiz_sid":"<quiz_uuid>","teacher_name":"Alice"}
{"action":"start_session","session_sid":"<session_uuid>"}
{"action":"finish_session","session_sid":"<session_uuid>"}
{"action":"get_results","session_sid":"<session_uuid>"}
```

Student flow:

```json
{"action":"join_session","join_code":"ABC123","student_name":"Bob"}
{"action":"submit_answer","participant_sid":"<participant_uuid>","question_sid":"<question_uuid>","answer_option_sid":"<answer_uuid>"}
```

Server events include `session_created`, `joined`, `participant_joined`,
`session_started`, `answer_saved`, `participant_progress`, `session_finished`,
`session_result`, and `error`.

Saved results are also available via `GET /api/session/{session_sid}/result`.
