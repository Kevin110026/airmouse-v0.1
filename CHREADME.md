# 前言
薛尹喆大電神把v0.0改成超讚的v0.1 ouob

# 系統需求
- 已安裝python
- 於系統終端執行 `pip install -r req.txt` 以安裝相關套件


# 使用須知:
    
按下 'esc' 或 'q' 以退出。


當 *Searching* 視窗彈出時，將您的手移至相機內。

接著，將您想用來控制滑鼠的手的大拇指彎曲，使系統辨識並追蹤您的手。

接著，您會看見*Matching* 視窗，表示系統已辨認出欲控制的手。

接著，保持大拇指彎曲並向四周稍微揮動您的手以利系統獲取您的手的詳細位置資訊。這個步驟將不會持續太久，煩請耐心等候。

當系統成功獲取位置後，*Controlling*視窗將彈出，代表您可以開始使用手來控制鼠標了!


彎曲全部手指會使系統從*Controlling*模式回到 *Searching*模式(此時手會看起來像貓掌一樣)。

系統將會自動退出*Controlling*模式如果相機已無法拍攝到擁有控制權的手。

## 啟動/移動
**大拇指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/07b40efc-ab69-474f-86ae-c3914ceeff9c.png" height="300">

拇指彎曲時滑鼠將會被拖動。

## 離開操控
**握拳:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/1e715ca9-dfa9-49d7-8911-34cf3a510f77.png" height="300">

在 *Controlling* 階段握拳以退出滑鼠操控。

## 左鍵 
**食指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/bca1da17-3192-429d-9e1d-a1b71815f14e.png" height="300">

彎曲握住，伸直釋放

快速彎曲伸直以點擊，跟一般滑鼠使用一樣。

## 雙擊 
**食指 (加中指):**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/f96d36cb-52e6-4c5d-96ba-c26d7464380e.png" height="300">

第一種方法 : 快速彎曲伸直食指兩次。

第二種方法 : 彎曲食指後，彎曲中指。
        
`因為快速彎曲食指兩次在低FPS情況很難做到，所以加上中指`

## 右鍵
**中指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/c285683e-48cd-4792-a5b3-0db260c75149.png" height="300">

彎曲握住，伸直釋放。

快速彎曲伸直使用右鍵，跟一般滑鼠使用一樣。

## 中鍵 
**中指 加 無名指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/275e5869-2365-40b0-aa11-8e7c5d088359.png" height="300">

彎曲中指跟無名指，使用中鍵。

## 滾輪
**無名指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/8e66b27f-0ecf-4ff5-bd3c-6037c0e5423f.png" height="300">

彎曲無名指，接著移動手掌，以滾動。

滑鼠在滾動時無法移動。

## 縮放
**大拇指 加 無名指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/ed3a037c-36f7-4045-b720-33fad647965d.png" height="300">

彎曲大拇指跟無名指，接著上/下移動手掌，以放大/縮小螢幕畫面。

## 靈敏度調整 
**食指 加 中指 加 無名指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/77a33f9c-2045-47c8-9cf8-0141ce11adee.png" height="300">

彎曲食指、中指跟無名指，接著上/下移動手掌，以調整靈敏度高/低。

## 慢速模式
**小拇指:**
<img src="https://github.com/Kevin110026/airmouse-v0.1/assets/131368612/a72c7181-3fe1-4471-8a16-da0a778c84fd.png" height="300">

彎曲小拇指，滑鼠將會放慢移動速度。

可以在 '移動'、'滾輪'、'縮放'、'靈敏度調整' 時添加使用。



# 常見問題:

## 相機

`Exception: Unable to access camera, please check README.md for more info`

檢查相機是否連接，或是權限是否被拒絕。 

您也可以嘗試將 `CAM_NUM` 中的 main.py(第15行) 變更為 1 或 2 (根據您相機的 id)
