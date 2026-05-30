import { Text } from '@fluentui/react-components';
import { CitationItem } from './CitationItem';
import type { ParsedCitation } from '../utils/parser';

interface CitationListProps {
  citations: ParsedCitation[];
  onInsert: (citation: ParsedCitation) => void;
  isInserting?: boolean;
  insertingId?: number | null;
  isOfficeReady?: boolean;
}

export function CitationList({ citations, onInsert, isInserting, insertingId, isOfficeReady }: CitationListProps) {
  if (citations.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Text style={{ color: '#605e5c', fontSize: '14px' }}>
          输入引用文献后，点击"解析"按钮生成引用选项
        </Text>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <Text style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
        引用选项（共 {citations.length} 条）
      </Text>
      {citations.map((citation) => (
        <CitationItem
          key={citation.id}
          citation={citation}
          onInsert={onInsert}
          isInserting={isInserting && insertingId === citation.id}
          disabled={!isOfficeReady}
        />
      ))}
    </div>
  );
}
