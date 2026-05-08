# Prompt Personas

This folder stores plain text prompt files for each AI persona.

## How It Works

The app reads `PERSONA_NAME` from `.env` and loads two files:

- `<persona>_system.txt`
- `<persona>_user.txt`

Example:

```env
PERSONA_NAME=cohost
```

This loads:

- `cohost_system.txt`
- `cohost_user.txt`

If you change it to:

```env
PERSONA_NAME=hype
```

the app loads:

- `hype_system.txt`
- `hype_user.txt`

## Adding A New Persona

To create a new persona called `analyst`, add:

- `analyst_system.txt`
- `analyst_user.txt`

Then set this in `.env`:

```env
PERSONA_NAME=analyst
```

## Prompt Notes

- Put the personality and behavior rules in the `*_system.txt` file.
- Put the user-facing template in the `*_user.txt` file.
- Keep `{transcript}` in the user prompt so the app can insert live speech.
- You do not need to edit Python to change wording or add personas.
