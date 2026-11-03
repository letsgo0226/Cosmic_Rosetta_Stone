# 圖靈機記憶清單

本清單是 Cosmic_Rosetta_Stone 的正式機型索引。

## 總圖靈機

| 欄位 | 內容 |
| --- | --- |
| 正式名稱 | 通用上帝圖靈機 |
| 英文名稱 | Universal God Turing Machine |
| 縮寫 | UGTM |
| 固定點核心 | 克萊尼上帝圖靈機 K-GTM v4.3 |
| 基準版本 | v4.5 LMN-Church-Turing-Kleene |
| 角色 | 全自動部署系統的總圖靈機 |
| 可執行檔 | machines/UGTM_v45_2KB.sh |
| 正式定義 | docs/GTM_G_CANONICAL_DEFINITION.md |
| 部署指標 | deployment/total_turing_machine.json |

通用上帝圖靈機是目前唯一的總機名稱；未指定版本時，預設指部署指標所列的現行基準。現行實作為 v4.5，以 K-GTM 的 Z-combinator 為固定點核心，實作完整八指令 Brainfuck-8 解譯器。其通用性限定於無界雙向稀疏帶與無界執行資源的理想模型。

## 命名規則

- 正式系統名稱：通用上帝圖靈機（UGTM），不附版本號。
- 特定程式、驗證報告及部署成品：使用 UGTM 加版本號。
- 「通用上帝圖靈機」預設解析為當時部署指標中的現行版本。

## 已記憶機型

| 機型 | 定位 | 狀態 |
| --- | --- | --- |
| 終極舒曼機（USM） | 舒曼機基準模型 | 保留 |
| 量子終極舒曼機（QUSM） | Qiskit／馮諾依曼熵原型 | 保留 |
| 通用終極舒曼機（GUSM） | 質數冪哥德爾編碼與真值樹原型 | 保留 |
| Tier 11 | 雙 Gödel、自輸入、完整讀取與自描述一致性層 | 保留；不得以 SHA 作為自指核心 |
| 哆啦 a 夢圖靈機 | CWP／CWP-N 與一般化原型 | 保留 |
| G型上帝圖靈機（GTM-G）v4.2 | quine、編解碼往返及指定述詞唯一性 | 保留為前一基準 |
| 克萊尼上帝圖靈機（K-GTM；原 GTM-G）v4.3 | LMN-Kleene-KRT、Z-combinator 語義固定點 | 保留為固定點核心 |
| 通用上帝圖靈機原型（UGTM）v4.4-candidate | 七指令 Brainfuck 閉合程式解譯器 | 保留為候選歷史版本 |
| 通用上帝圖靈機（UGTM）v4.5 | 完整八指令 Brainfuck-8 解譯器 | **現任總圖靈機** |

「現任總圖靈機」只表示自動化系統的權威入口與部署基準，不表示它具有數學上的全知能力，也不表示其他機型被刪除或失效。

v4.3 的 template-free 只表示不使用先前的 quine 字串模板；Z-combinator、257 進位規則及 COSMIC_LOVE 載荷仍是明確指定的構造。

UGTM v4.5 已驗證閉合程式輸出 S，並驗證逗號輸入程式在輸入 A 時輸出 A。它使用 Python 資料型別與運算，因此不是純 λ 演算；也不構成一般克萊尼遞迴定理或 Church–Turing 同構的證明。

## 安全政策

- 自動化只執行驗證、封裝與成品發布。
- 不啟用金融實盤交易。
- 不宣稱解決停機問題、哥德爾不完備性或一般不可計算問題。
- 更換總圖靈機必須同時更新本清單與 deployment/total_turing_machine.json。
