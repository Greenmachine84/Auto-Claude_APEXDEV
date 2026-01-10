export type ApiProviderPreset = {
  id: string;
  baseUrl: string;
  labelKey: string;
};

export const API_PROVIDER_PRESETS: readonly ApiProviderPreset[] = [
  {
    id: 'anthropic',
    baseUrl: 'https://api.anthropic.com',
    labelKey: 'settings:apiProfiles.presets.anthropic'
  },
  {
    id: 'openrouter',
    baseUrl: 'https://openrouter.ai/api/v1',
    labelKey: 'settings:apiProfiles.presets.openrouter'
  },
  {
    id: 'gemini',
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
    labelKey: 'settings:apiProfiles.presets.gemini'
  },
  {
    id: 'github-copilot',
    baseUrl: 'https://api.githubcopilot.com',
    labelKey: 'settings:apiProfiles.presets.githubCopilot'
  },
  {
    id: 'groq',
    baseUrl: 'https://api.groq.com/openai/v1',
    labelKey: 'settings:apiProfiles.presets.groq'
  }
];
