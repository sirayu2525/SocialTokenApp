import nfc
import binascii

def on_connect(tag: nfc.tag.Tag) -> bool:
    try:
        print("connected")
        tag_data = tag.dump()
        print(tag_data)
        #print(tag_data[3].split('|')[1])
        #print(tag_data[7].split('|')[1])
        print("\n".join(tag_data))
        idm = binascii.hexlify(tag._nfcid)
        print("IDm : " + str(idm.decode()))
        IDm = str(idm.decode())
    except:
        print('::ERROR::')

    return True  # Trueを返しておくとタグが存在しなくなるまで待機され、離すとon_releaseが発火する

def on_release(tag: nfc.tag.Tag) -> None:
    print("released")
    #flag = False

with nfc.ContactlessFrontend("usb") as clf:
    while True:
        clf.connect(rdwr={"on-connect": on_connect, "on-release": on_release})