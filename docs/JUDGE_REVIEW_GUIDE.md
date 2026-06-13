# Judge Review Guide

## Fast Path

1. Start backend and frontend with `.env.demo`.
2. Open the React dashboard.
3. Click `Run Judge Demo`.
4. Watch the agent flow, metrics contradiction, reasoning timeline, Microsoft IQ proof panel, remediation plan, and manager summary.

## What To Verify

- The demo runs without Azure credentials.
- `/iq/status` is honest about live Microsoft IQ.
- `/demo/run` includes evidence, uncertainty, confidence, and narration.
- The frontend shows agents thinking, not only a final paragraph.
- OpenAI fallback, if configured, is labeled as fallback reasoning only.

## Best Screen To Show

Animated Agent Flow.
