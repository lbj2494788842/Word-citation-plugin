import { useState } from 'react';
import { Button, Divider, Text, Spinner } from '@fluentui/react-components';
import { ArrowSync24Regular, Book24Regular } from '@fluentui/react-icons';
import { CitationInput } from './components/CitationInput';
import { CitationList } from './components/CitationList';
import { parseCitations, type ParsedCitation } from './utils/parser';
import { useFootnoteInserter } from './hooks/useFootnoteInserter';
import './App.css';

export function App() {
  const [inputText, setInputText] = useState('');
  const [citations, setCitations] = useState<ParsedCitation[]>([]);
  const [insertingId, setInsertingId] = useState<number | null>(null);

  const { insertFootnote, isInserting, error, clearError, isOfficeReady } = useFootnoteInserter();

  const handleParse = () => {
    const parsed = parseCitations(inputText);
    setCitations(parsed);
  };

  const handleInsert = async (citation: ParsedCitation) => {
    if (!isOfficeReady) {
      return;
    }
    setInsertingId(citation.id);
    clearError();
    await insertFootnote(citation.text);
    setInsertingId(null);
  };

  // 在 Word 外调试时显示提示
  const showOfficeWarning = !isOfficeReady && !window.Office;

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-title">
          <Book24Regular style={{ fontSize: '24px', marginRight: '8px' }} />
          <Text weight="semibold" size={500}>Word 引用插入</Text>
        </div>
        <Text style={{ color: '#605e5c', fontSize: '12px' }}>
          在 Word 中快速插入参考文献脚注
        </Text>
      </header>

      {showOfficeWarning && (
        <div className="info-banner">
          <span>💡 此插件需要在 Word 中运行。当前为预览模式，插入脚注功能不可用。</span>
        </div>
      )}

      {!isOfficeReady && window.Office && (
        <div className="info-banner loading">
          <Spinner size="tiny" />
          <span>正在连接 Word...</span>
        </div>
      )}

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={clearError} className="error-close">×</button>
        </div>
      )}

      <section className="input-section">
        <CitationInput
          value={inputText}
          onChange={setInputText}
        />
        <Button
          icon={<ArrowSync24Regular />}
          onClick={handleParse}
          disabled={!inputText.trim()}
          appearance="primary"
          style={{ width: '100%', marginTop: '8px' }}
        >
          解析引用
        </Button>
      </section>

      <Divider />

      <section className="list-section">
        <CitationList
          citations={citations}
          onInsert={handleInsert}
          isInserting={isInserting}
          insertingId={insertingId}
          isOfficeReady={isOfficeReady}
        />
      </section>

      <footer className="app-footer">
        <Text style={{ fontSize: '11px', color: '#a19f9d' }}>
          {isOfficeReady
            ? '点击引用选项即可插入脚注到光标位置'
            : '等待 Word 连接就绪...'}
        </Text>
      </footer>
    </div>
  );
}
