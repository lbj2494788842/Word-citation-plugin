import { Textarea, Button } from '@fluentui/react-components';
import { Copy24Regular, ArrowSync24Regular } from '@fluentui/react-icons';
import { copyToClipboard } from '../utils/parser';

interface CitationInputProps {
  value: string;
  onChange: (value: string) => void;
}

export function CitationInput({ value, onChange }: CitationInputProps) {
  const handleCopy = async () => {
    try {
      await copyToClipboard(value);
    } catch {
      console.error('复制失败');
    }
  };

  const handleClear = () => {
    onChange('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <Textarea
        value={value}
        onChange={(_, data) => onChange(data.value)}
        placeholder="在此粘贴引用文献内容，每行一条引用..."
        style={{ minHeight: '200px', fontFamily: 'system-ui' }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          icon={<Copy24Regular />}
          onClick={handleCopy}
          disabled={!value}
          appearance="secondary"
        >
          一键复制
        </Button>
        <Button
          icon={<ArrowSync24Regular />}
          onClick={handleClear}
          disabled={!value}
          appearance="secondary"
        >
          清空
        </Button>
      </div>
    </div>
  );
}
