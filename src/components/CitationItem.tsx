import { Card, Text, Badge } from '@fluentui/react-components';
import { TextDescription24Regular } from '@fluentui/react-icons';
import type { ParsedCitation } from '../utils/parser';

interface CitationItemProps {
  citation: ParsedCitation;
  onInsert: (citation: ParsedCitation) => void;
  isInserting?: boolean;
  disabled?: boolean;
}

export function CitationItem({ citation, onInsert, isInserting, disabled }: CitationItemProps) {
  return (
    <Card
      style={{
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'background-color 0.2s',
        padding: '12px',
        border: '1px solid #e0e0e0',
        borderRadius: '6px',
        opacity: disabled ? 0.7 : 1
      }}
      onClick={() => !isInserting && !disabled && onInsert(citation)}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <Badge
          appearance="filled"
          color="informative"
          style={{ flexShrink: 0 }}
        >
          {citation.id}
        </Badge>
        <Text
          style={{
            flex: 1,
            fontSize: '14px',
            lineHeight: '1.5',
            wordBreak: 'break-word'
          }}
        >
          {citation.text}
        </Text>
        <TextDescription24Regular
          style={{
            flexShrink: 0,
            color: isInserting ? '#0078d4' : '#605e5c',
            fontSize: '20px'
          }}
        />
      </div>
    </Card>
  );
}
