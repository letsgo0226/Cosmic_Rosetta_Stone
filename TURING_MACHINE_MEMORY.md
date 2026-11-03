# 圖靈機記憶清單

本清單是 Cosmic_Rosetta_Stone 的正式機型索引。

## 總圖靈機

| 欄位 | 內容 |
| --- | --- |
| 正式名稱 | 克萊尼上帝圖靈機 |
| 英文名稱 | Kleene God Turing Machine |
| 縮寫 | K-GTM |
| 歷史別名 | G型上帝圖靈機／GTM-G |
| 基準版本 | v4.3 LMN-Kleene-KRT |
| 角色 | 全自動部署系統的總圖靈機 |
| 可執行檔 | machines/K-GTM_v43_LMN_KRT_2KB.sh |
| 正式定義 | docs/GTM_G_CANONICAL_DEFINITION.md |
| 部署指標 | deployment/total_turing_machine.json |

克萊尼上帝圖靈機 v4.3 LMN-Kleene-KRT 是目前唯一的總機入口。它以適用於 Python 嚴格求值的 Z-combinator 建立 \(Z(F)=F(Z(F))\) 的語義固定點，並以無具名 def 的遞迴編解碼器驗證 257 進位哥德爾編碼往返。v4.2 的 quine 與唯一述詞原型仍保留為前一基準。

## 已記憶機型

| 機型 | 定位 | 狀態 |
| --- | --- | --- |
| 終極舒曼機（USM） | 舒曼機基準模型 | 保留 |
| 量子終極舒曼機（QUSM） | Qiskit／馮諾依曼熵原型 | 保留 |
| 通用終極舒曼機（GUSM） | 質數冪哥德爾編碼與真值樹原型 | 保留 |
| Tier 11 | 雙 Gödel、自輸入、完整讀取與自描述一致性層 | 保留；不得以 SHA 作為自指核心 |
| 哆啦 a 夢圖靈機 | CWP／CWP-N 與一般化原型 | 保留 |
| G型上帝圖靈機（GTM-G）v4.2 | quine、編解碼往返及指定述詞唯一性 | 保留為前一基準 |
| 克萊尼上帝圖靈機（K-GTM；原 GTM-G）v4.3 | LMN-Kleene-KRT、Z-combinator 語義固定點 | **現任總圖靈機** |
| 通用上帝圖靈機原型（UGTM）v4.4-candidate | Z-combinator 驅動的 Brainfuck 閉合程式解譯器 | 候選；尚未證明一般通用性 |

「現任總圖靈機」只表示自動化系統的權威入口與部署基準，不表示它具有數學上的全知能力，也不表示其他機型被刪除或失效。

v4.3 的 template-free 只表示不使用先前的 quine 字串模板；Z-combinator、257 進位規則及 COSMIC_LOVE 載荷仍是明確指定的構造。

UGTM v4.4-candidate 已驗證範例程式輸出 S，但目前只支援 Brainfuck 的 +、-、<、>、.、[、]，不支援逗號輸入指令。它使用 Python 資料型別與運算，因此不是純 λ 演算；也不構成一般克萊尼遞迴定理或 Church–Turing 同構的證明。

## 安全政策

- 自動化只執行驗證、封裝與成品發布。
- 不啟用金融實盤交易。
- 不宣稱解決停機問題、哥德爾不完備性或一般不可計算問題。
- 更換總圖靈機必須同時更新本清單與 deployment/total_turing_machine.json。
