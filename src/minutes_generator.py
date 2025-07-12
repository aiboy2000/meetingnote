"""
議事録生成器
転写テキストから要約と行動項目を抽出
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MinutesGenerator:
    def __init__(self, use_local_llm: bool = True):
        """
        議事録生成器を初期化
        
        Args:
            use_local_llm: ローカルLLMを使用するか
        """
        self.use_local_llm = use_local_llm
        
        # 行動項目を示すキーワード
        self.action_keywords = [
            '検討', '確認', '調整', '実施', '対応', '準備', '作成',
            '提出', '報告', '連絡', '相談', '決定', '承認', '修正'
        ]
        
        # 決定事項を示すキーワード  
        self.decision_keywords = [
            '決定', '承認', '採用', '選定', '確定', '合意', '了承'
        ]
        
        # 課題を示すキーワード
        self.issue_keywords = [
            '課題', '問題', '懸念', '検討事項', '要確認', '要検討', '要調整'
        ]
    
    def generate_minutes(self, transcript: str, meeting_info: Dict = None) -> Dict:
        """
        転写テキストから議事録を生成
        
        Args:
            transcript: 転写テキスト
            meeting_info: 会議情報（日時、参加者など）
            
        Returns:
            構造化された議事録
        """
        logger.info("Generating meeting minutes...")
        
        # 基本的な議事録構造を作成
        minutes = {
            "meeting_info": meeting_info or {},
            "summary": self._generate_summary(transcript),
            "decisions": self._extract_decisions(transcript),
            "action_items": self._extract_action_items(transcript),
            "issues": self._extract_issues(transcript),
            "participants": self._extract_participants(transcript),
            "key_topics": self._extract_key_topics(transcript),
            "generated_at": datetime.now().isoformat()
        }
        
        return minutes
    
    def _generate_summary(self, transcript: str) -> str:
        """
        会議の要約を生成
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            要約テキスト
        """
        if self.use_local_llm:
            return self._local_summarize(transcript)
        else:
            return self._rule_based_summary(transcript)
    
    def _local_summarize(self, transcript: str) -> str:
        """
        ローカルLLMを使用した要約（実装予定）
        """
        # TODO: OllamaなどのローカルLLMとの連携実装
        return self._rule_based_summary(transcript)
    
    def _rule_based_summary(self, transcript: str) -> str:
        """
        ルールベースの簡易要約
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            要約
        """
        # 文を分割
        sentences = re.split(r'[。！？]', transcript)
        
        # 重要そうな文を抽出
        important_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # 短すぎる文は除外
                # 重要キーワードを含む文を優先
                score = 0
                for keyword in self.decision_keywords + self.action_keywords:
                    if keyword in sentence:
                        score += 1
                
                if score > 0:
                    important_sentences.append((sentence, score))
        
        # スコア順にソートして上位を選択
        important_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in important_sentences[:5]]
        
        return '。'.join(top_sentences) + '。'
    
    def _extract_decisions(self, transcript: str) -> List[Dict]:
        """
        決定事項を抽出
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            決定事項のリスト
        """
        decisions = []
        sentences = re.split(r'[。！？]', transcript)
        
        for sentence in sentences:
            sentence = sentence.strip()
            for keyword in self.decision_keywords:
                if keyword in sentence and len(sentence) > 5:
                    decision = {
                        "content": sentence,
                        "keyword": keyword,
                        "type": "decision"
                    }
                    decisions.append(decision)
                    break
        
        return decisions
    
    def _extract_action_items(self, transcript: str) -> List[Dict]:
        """
        行動項目を抽出
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            行動項目のリスト
        """
        action_items = []
        sentences = re.split(r'[。！？]', transcript)
        
        for sentence in sentences:
            sentence = sentence.strip()
            for keyword in self.action_keywords:
                if keyword in sentence and len(sentence) > 5:
                    # 担当者を抽出（簡易版）
                    assignee = self._extract_assignee(sentence)
                    
                    action_item = {
                        "content": sentence,
                        "keyword": keyword,
                        "assignee": assignee,
                        "type": "action_item",
                        "status": "pending"
                    }
                    action_items.append(action_item)
                    break
        
        return action_items
    
    def _extract_issues(self, transcript: str) -> List[Dict]:
        """
        課題・問題点を抽出
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            課題のリスト
        """
        issues = []
        sentences = re.split(r'[。！？]', transcript)
        
        for sentence in sentences:
            sentence = sentence.strip()
            for keyword in self.issue_keywords:
                if keyword in sentence and len(sentence) > 5:
                    issue = {
                        "content": sentence,
                        "keyword": keyword,
                        "type": "issue",
                        "priority": self._assess_priority(sentence)
                    }
                    issues.append(issue)
                    break
        
        return issues
    
    def _extract_participants(self, transcript: str) -> List[str]:
        """
        参加者を抽出（簡易版）
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            参加者のリスト
        """
        # 敬語や肩書きのパターンから参加者を推測
        participant_patterns = [
            r'(\w+)さん',
            r'(\w+)部長',
            r'(\w+)課長',
            r'(\w+)主任',
            r'(\w+)係長'
        ]
        
        participants = set()
        for pattern in participant_patterns:
            matches = re.findall(pattern, transcript)
            participants.update(matches)
        
        return list(participants)
    
    def _extract_key_topics(self, transcript: str) -> List[str]:
        """
        主要トピックを抽出
        
        Args:
            transcript: 転写テキスト
            
        Returns:
            トピックのリスト
        """
        # 建築関連の主要トピックキーワード
        topic_keywords = [
            '工事', '設計', '施工', '材料', '品質', '安全', '工程',
            '予算', '契約', '検査', '図面', '仕様', '基準'
        ]
        
        topics = []
        for keyword in topic_keywords:
            if keyword in transcript:
                # キーワード周辺の文脈を抽出
                context = self._extract_context(transcript, keyword)
                if context:
                    topics.append({
                        "keyword": keyword,
                        "context": context
                    })
        
        return topics
    
    def _extract_assignee(self, sentence: str) -> Optional[str]:
        """
        文から担当者を抽出
        
        Args:
            sentence: 対象の文
            
        Returns:
            担当者名
        """
        # 簡易的な担当者抽出
        assignee_patterns = [
            r'(\w+)さんが',
            r'(\w+)部長が',
            r'(\w+)で'
        ]
        
        for pattern in assignee_patterns:
            match = re.search(pattern, sentence)
            if match:
                return match.group(1)
        
        return None
    
    def _assess_priority(self, sentence: str) -> str:
        """
        文の優先度を評価
        
        Args:
            sentence: 対象の文
            
        Returns:
            優先度 (high/medium/low)
        """
        high_priority_words = ['緊急', '至急', '重要', '必須']
        medium_priority_words = ['要確認', '要検討', '課題']
        
        for word in high_priority_words:
            if word in sentence:
                return 'high'
        
        for word in medium_priority_words:
            if word in sentence:
                return 'medium'
        
        return 'low'
    
    def _extract_context(self, transcript: str, keyword: str, window: int = 50) -> str:
        """
        キーワード周辺の文脈を抽出
        
        Args:
            transcript: 全文
            keyword: キーワード
            window: 前後の文字数
            
        Returns:
            文脈
        """
        index = transcript.find(keyword)
        if index == -1:
            return ""
        
        start = max(0, index - window)
        end = min(len(transcript), index + len(keyword) + window)
        
        return transcript[start:end].strip()
    
    def export_minutes(self, minutes: Dict, output_path: str, format: str = "json"):
        """
        議事録をファイルに出力
        
        Args:
            minutes: 議事録データ
            output_path: 出力パス
            format: 出力形式 (json/text)
        """
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(minutes, f, ensure_ascii=False, indent=2)
        
        elif format == "text":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._format_minutes_text(minutes))
        
        logger.info(f"Minutes exported to {output_path}")
    
    def _format_minutes_text(self, minutes: Dict) -> str:
        """
        議事録をテキスト形式にフォーマット
        
        Args:
            minutes: 議事録データ
            
        Returns:
            フォーマットされたテキスト
        """
        lines = []
        lines.append("=" * 50)
        lines.append("議事録")
        lines.append("=" * 50)
        lines.append("")
        
        # 会議情報
        if minutes.get("meeting_info"):
            lines.append("【会議情報】")
            for key, value in minutes["meeting_info"].items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        # 要約
        lines.append("【要約】")
        lines.append(minutes.get("summary", ""))
        lines.append("")
        
        # 決定事項
        if minutes.get("decisions"):
            lines.append("【決定事項】")
            for i, decision in enumerate(minutes["decisions"], 1):
                lines.append(f"  {i}. {decision['content']}")
            lines.append("")
        
        # 行動項目
        if minutes.get("action_items"):
            lines.append("【行動項目】")
            for i, item in enumerate(minutes["action_items"], 1):
                assignee = f" ({item['assignee']})" if item.get('assignee') else ""
                lines.append(f"  {i}. {item['content']}{assignee}")
            lines.append("")
        
        # 課題
        if minutes.get("issues"):
            lines.append("【課題・検討事項】")
            for i, issue in enumerate(minutes["issues"], 1):
                priority = f" [{issue['priority']}]" if issue.get('priority') else ""
                lines.append(f"  {i}. {issue['content']}{priority}")
            lines.append("")
        
        lines.append(f"生成日時: {minutes.get('generated_at', '')}")
        
        return '\n'.join(lines)

def main():
    """テスト実行"""
    generator = MinutesGenerator()
    
    # サンプル転写テキスト
    sample_transcript = """
    本日の会議では、RC構造の基礎工事について検討しました。
    田中部長から品質管理の重要性について説明がありました。
    施工図面の修正が必要であることが決定されました。
    山田さんが来週までに図面を確認することになりました。
    安全管理についても課題があることが判明しました。
    """
    
    # 議事録生成
    minutes = generator.generate_minutes(sample_transcript)
    
    # 結果を表示
    print(json.dumps(minutes, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()