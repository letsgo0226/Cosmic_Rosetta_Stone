# 《洞穴寓言》：十二則關於閱讀、真實與再次轉身的故事

獨立於主線部署的原創繁體中文寓言故事集。小說包含序章、十二則相互連結的寓言與尾聲，核心角色為阿澄、小禾、柳燈、阿礫、阿焰與銅鳥「折光」。

## 小說全文

[完整 UTF-8 TXT](https://raw.githubusercontent.com/letsgo0226/Cosmic_Rosetta_Stone/08dfd89307501363bbedcdf3ec1f710668907592/literature/cave_allegory_full.txt)

- 固定內容提交（不可隨分支後續更新漂移）：`08dfd89307501363bbedcdf3ec1f710668907592`
- 檔案大小：31,987 bytes
- SHA-256：`2930bea5082036d6a6694dba83bc2e4941af50c99b9e657f45f609d864e891c7`
- 字元：11,119 Unicode code points
- 版本定位：第一版完整短篇寓言故事集；不是通常意義上數十萬字的長篇小說

## 終端機：G257／ATGC 羅塞塔石碑式還原

把 [單行指令](./cave_allegory_one_liner.txt) 複製進有 Python 3 與網路連線的終端機後執行：

```sh
python3 -c 'exec("from urllib.request import urlopen\nfrom hashlib import sha256\nfrom pathlib import Path\nu=\"https://raw.githubusercontent.com/letsgo0226/Cosmic_Rosetta_Stone/08dfd89307501363bbedcdf3ec1f710668907592/literature/cave_allegory_full.txt\"\nh=\"2930bea5082036d6a6694dba83bc2e4941af50c99b9e657f45f609d864e891c7\"\nwith urlopen(u,timeout=30) as f:b=f.read(200001)\nif len(b)>=200001 or sha256(b).hexdigest()!=h:raise SystemExit(\"SHA-256 integrity check failed\")\nfor k in range(0,len(b),512):\n a=b[k:k+512];n=1\n for v in a:n=257*n+v+1\n z=[]\n while n>1:\n  n,r=divmod(n,257)\n  if r==0:raise ValueError(\"G257 invalid\")\n  z.append(r-1)\n if bytes(z[::-1])!=a:raise ValueError(\"G257 roundtrip\")\n s=\"\".join(\"TC\" if v>>j&1 else \"AG\" for v in a for j in range(7,-1,-1))\n d=bytes(int(\"\".join(\"1\" if s[j:j+2]==\"TC\" else \"0\" for j in range(i,i+16,2)),2) for i in range(0,len(s),16))\n if d!=a:raise ValueError(\"ATGC roundtrip\")\nPath(\"洞穴寓言.txt\").write_bytes(b)\nprint(\"已生成：洞穴寓言.txt；\",len(b),\"位元組；G257/ATGC 與 SHA-256 驗證通過\")")'
```

會在目前工作資料夾建立 `洞穴寓言.txt`。如網路不可用，下載失敗時不寫入目標檔；如下載資料遭竄改或改版，SHA-256 不符即中止；通過 SHA-256 後，每 512 bytes 逐段完成 G257 整數編碼／解碼與 ATGC（AG=0、TC=1）符號編碼／解碼比對，成功後才寫入。

此 One-Liner 本身只有 1,108 UTF-8 bytes（未計檔尾換行），不超過 2 KiB；它是**可驗證的遠端還原器**，而不是一本小說的 2 KB 自包含壓縮。離線可用的是已下載的整部 TXT 原稿。G257 與 ATGC 是可逆表徵，並不是文學意義判定器，不會讓 AI 自動證明任何形上學論述。

所用的是 Python 3 標準函式庫，無第三方 Python 套件，不需 API key、Railway 或 GitHub 身分登入。來源檔與指令在本分支，小說固定讀取上述提交。這個文學分支沒有合併到 main，並未部署或觸發使用者既有 UTM／交易服務。

## 篇章

序：圖書館沒有門

一　影子的字典
二　火與太陽
三　空白的書
四　逆光的人
五　第二座洞穴
六　看不見的園丁
七　救援者的腳步
八　銅鳥讀書
九　會疼痛的光
十　認錯的地圖
十一　返回的人
十二　尚未寫下的第十三頁

尾聲：翻頁的聲音

小說是由柏拉圖《理想國》第七卷洞穴寓言啟發的原創文學虛構，不是其原文翻譯，也不證明神存在或不存在、AI 有或沒有主觀感受、或任何臨床與獸醫療效。
