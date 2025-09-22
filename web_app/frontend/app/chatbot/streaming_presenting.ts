// streaming_presenting.ts
// For presenting streaming results, formatting, and separators

export const SEP = "\n\n------------------------\n\n";

export function formatAgentOutput(text: string, agent?: string, lastAgent?: string): string {
  // Add separator if agent changes
  if (agent && lastAgent && agent !== lastAgent) {
    return SEP + text;
  }
  return text;
}

// Add more formatting/presenting helpers as needed
