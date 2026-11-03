# Cosmic_Rosetta_Stone

本倉庫以 **通用上帝圖靈機（Universal God Turing Machine；UGTM）** 作為全自動部署系統的總圖靈機。現行實作為 v4.5 LMN-Church-Turing-Kleene；K-GTM v4.3 保留為其固定點核心。

- [圖靈機記憶清單](TURING_MACHINE_MEMORY.md)
- [克萊尼上帝圖靈機正式定義](docs/GTM_G_CANONICAL_DEFINITION.md)
- [總圖靈機部署指標](deployment/total_turing_machine.json)
- [UGTM v4.5 單行實作](machines/UGTM_v45_2KB.sh)
- [UGTM 通用性範圍](docs/UGTM_UNIVERSALITY_SCOPE.md)
- [K-GTM v4.3 固定點核心](machines/K-GTM_v43_LMN_KRT_2KB.sh)
- [GTM-G v4.2 quine 基準](machines/GTM-G_v42_2KB.sh)

每次相關檔案推送至 main 時，GitHub Actions 會自動驗證完整八指令語義、閉合程式輸出、輸入指令、總機指標與安全標記，然後發布可下載的已驗證成品。
