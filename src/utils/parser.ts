export interface ParsedCitation {
  id: number;
  text: string;
  originalText: string;
}

export function parseCitations(input: string): ParsedCitation[] {
  const result: ParsedCitation[] = [];
  
  const cleanedInput = input.trim();
  
  const citationRegex = /\[(\d+)\]([^\[]*(?:\[[^\d][^\[]*\][^\[]*)*)/g;
  
  let match;
  while ((match = citationRegex.exec(cleanedInput)) !== null) {
    const id = parseInt(match[1], 10);
    const text = match[2].trim();
    
    if (text.length > 0) {
      result.push({
        id,
        text,
        originalText: `[${id}]${text}`
      });
    }
  }
  
  if (result.length === 0) {
    const lines = cleanedInput.split('\n').filter(line => line.trim().length > 0);
    lines.forEach((line, index) => {
      const originalText = line.trim();
      const cleanedText = originalText.replace(/^\[\d+\]\s*/, '').trim();
      if (cleanedText.length > 0) {
        result.push({
          id: index + 1,
          text: cleanedText,
          originalText
        });
      }
    });
  }
  
  return result.sort((a, b) => a.id - b.id);
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}
