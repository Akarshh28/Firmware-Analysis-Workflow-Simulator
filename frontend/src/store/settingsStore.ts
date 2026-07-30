import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  apiKeys: {
    virusTotal: string;
    openAI: string;
    ghidraUrl: string;
  };
  ui: {
    theme: 'dark' | 'light';
    compactMode: boolean;
  };
  updateApiKey: (key: keyof SettingsState['apiKeys'], value: string) => void;
  updateUI: <K extends keyof SettingsState['ui']>(key: K, value: SettingsState['ui'][K]) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      apiKeys: {
        virusTotal: '',
        openAI: '',
        ghidraUrl: 'http://localhost:1337',
      },
      ui: {
        theme: 'dark',
        compactMode: false,
      },
      updateApiKey: (key, value) =>
        set((state) => ({
          apiKeys: { ...state.apiKeys, [key]: value },
        })),
      updateUI: (key, value) =>
        set((state) => ({
          ui: { ...state.ui, [key]: value },
        })),
    }),
    {
      name: 'faws-settings',
    }
  )
);
