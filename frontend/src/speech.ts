type SpeechRecognitionResultEvent = Event & {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      length: number;
      [index: number]: {transcript: string};
    };
  };
};

type SpeechRecognitionErrorEvent = Event & {error?: string; message?: string};

type SpeechRecognition = EventTarget & {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: SpeechRecognitionResultEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type SpeechWindow = Window & {
  SpeechRecognition?: new () => SpeechRecognition;
  webkitSpeechRecognition?: new () => SpeechRecognition;
};

export function canUseBrowserSpeech(): boolean {
  const speechWindow = window as SpeechWindow;
  return Boolean(speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition);
}

export function startBrowserSpeech(onTranscript: (text: string) => void, onError: (error: Error) => void): () => void {
  const speechWindow = window as SpeechWindow;
  const SpeechRecognition = speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
  if (!SpeechRecognition) throw new Error('Reconhecimento de voz do navegador indisponível. Use Chrome ou Edge.');

  const recognition = new SpeechRecognition();
  let stopped = false;
  recognition.lang = 'pt-BR';
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  recognition.onresult = event => {
    const parts: string[] = [];
    for (let index = event.resultIndex; index < event.results.length; index++) {
      const result = event.results[index];
      if (result.isFinal && result[0]?.transcript) parts.push(result[0].transcript);
    }
    const text = parts.join(' ').trim();
    if (text) onTranscript(text);
  };
  recognition.onerror = event => {
    if (event.error === 'no-speech') return;
    onError(new Error(event.message || event.error || 'Falha no reconhecimento de voz do navegador.'));
  };
  recognition.onend = () => { stopped = true; };
  recognition.start();
  return () => {
    stopped = true;
    recognition.onend = null;
    recognition.stop();
  };
}
