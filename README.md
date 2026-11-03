# Cosmic_Rosetta_Stone

本倉庫目前以 **克萊尼上帝圖靈機（K-GTM）v4.3 LMN-Kleene-KRT** 作為全自動部署系統的總圖靈機。「G型上帝圖靈機／GTM-G」保留為歷史別名。

- [圖靈機記憶清單](TURING_MACHINE_MEMORY.md)
- [克萊尼上帝圖靈機正式定義](docs/GTM_G_CANONICAL_DEFINITION.md)
- [總圖靈機部署指標](deployment/total_turing_machine.json)
- [K-GTM v4.3 LMN-Kleene-KRT 單行實作](machines/K-GTM_v43_LMN_KRT_2KB.sh)
- [GTM-G v4.2 quine 基準](machines/GTM-G_v42_2KB.sh)

每次相關檔案推送至 main 時，GitHub Actions 會自動驗證 Z-combinator 語義固定點、哥德爾編解碼往返及總機指標，然後發布可下載的已驗證成品。
