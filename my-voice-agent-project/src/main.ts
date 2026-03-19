import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime';

const agent = new RealtimeAgent({
  name: 'Assistant',
  instructions: 'You are a helpful assistant.',
});

let session: RealtimeSession | null = null;

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div style="font-family: sans-serif; padding: 2rem; text-align: center;">
    <h1>Voice Agent</h1>
    <button id="connect-btn">Connect</button>
    <p id="status">Not connected</p>
  </div>
`;

const btn = document.querySelector<HTMLButtonElement>('#connect-btn')!;
const status = document.querySelector<HTMLParagraphElement>('#status')!;

btn.addEventListener('click', async () => {
  if (session) {
    session.close();
    session = null;
    btn.textContent = 'Connect';
    status.textContent = 'Disconnected';
    return;
  }

  btn.textContent = 'Connecting...';
  btn.disabled = true;

  try {
    // Fetch an ephemeral key from your backend (never expose your real API key here).
    // For local testing only, you can temporarily paste an ephemeral key (ek_...) directly.
    const res = await fetch('/api/session');
    const { apiKey } = await res.json();

    session = new RealtimeSession(agent);
    await session.connect({ apiKey });

    status.textContent = 'Connected — speak now!';
    btn.textContent = 'Disconnect';
  } catch (e) {
    console.error(e);
    status.textContent = `Error: ${(e as Error).message}`;
    btn.textContent = 'Connect';
  } finally {
    btn.disabled = false;
  }
});