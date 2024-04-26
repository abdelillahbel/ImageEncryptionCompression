import wx
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
import io

class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Photo Control')
        self.panel = wx.Panel(self.frame)
        self.PhotoMaxSize = 240
        self.key = get_random_bytes(16)  # Generate a random 128-bit key for AES encryption
        self.createWidgets()
        self.frame.Show()

    def createWidgets(self):
        instructions = 'Browse for an image'
        img = wx.Image(240, 240)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(img))
        instructLbl = wx.StaticText(self.panel, label=instructions)
        self.photoTxt = wx.TextCtrl(self.panel, size=(200, -1))
        browseBtn = wx.Button(self.panel, label='Browse')
        browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)

        # Add buttons for compress, encrypt, decrypt, and decompress
        compressBtn = wx.Button(self.panel, label='Compress')
        compressBtn.Bind(wx.EVT_BUTTON, self.compress)
        encryptBtn = wx.Button(self.panel, label='Encrypt')
        encryptBtn.Bind(wx.EVT_BUTTON, self.encrypt)
        decryptBtn = wx.Button(self.panel, label='Decrypt')
        decryptBtn.Bind(wx.EVT_BUTTON, self.decrypt)
        decompressBtn = wx.Button(self.panel, label='Decompress')
        decompressBtn.Bind(wx.EVT_BUTTON, self.decompress)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizer.Add(wx.StaticLine(self.panel, wx.ID_ANY), 0, wx.ALL | wx.EXPAND, 5)
        self.mainSizer.Add(instructLbl, 0, wx.ALL, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.sizer.Add(self.photoTxt, 0, wx.ALL, 5)
        self.sizer.Add(browseBtn, 0, wx.ALL, 5)
        self.sizer.Add(compressBtn, 0, wx.ALL, 5)
        self.sizer.Add(encryptBtn, 0, wx.ALL, 5)
        self.sizer.Add(decryptBtn, 0, wx.ALL, 5)
        self.sizer.Add(decompressBtn, 0, wx.ALL, 5)
        self.mainSizer.Add(self.sizer, 0, wx.ALL, 5)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.panel.Layout()

    def onBrowse(self, event):
        """
        Browse for file
        """
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        self.onView()

    def onView(self):
        filepath = self.photoTxt.GetValue()
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(int(NewW), int(NewH))
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()

    def compress(self, event):
        filepath = self.photoTxt.GetValue()
        # Compress the image
        img = Image.open(filepath)
        img.save("compressed.jpg", "JPEG", optimize=True, quality=30)
        wx.MessageBox('Image compressed successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.show_image("compressed.jpg")

    def encrypt(self, event):
        # Encrypt the compressed image
        with open("compressed.jpg", "rb") as f:
            plaintext = f.read()

        cipher = AES.new(self.key, AES.MODE_CBC)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

        with open("encrypted.jpg", "wb") as f:
            f.write(cipher.iv)
            f.write(ciphertext)

        wx.MessageBox('Image encrypted successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)

    def decrypt(self, event):
        # Decrypt the image
        with open("encrypted.jpg", "rb") as f:
            iv = f.read(16)
            ciphertext = f.read()

        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        with open("decrypted.jpg", "wb") as f:
            f.write(plaintext)

        wx.MessageBox('Image decrypted successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)
        self.show_image("decrypted.jpg")

    def decompress(self, event):
        filepath = self.photoTxt.GetValue()
        # Decompress the image
        img = Image.open("decrypted.jpg")
        img.save(filepath)

        os.remove("encrypted.jpg")  # Remove the encrypted image file
        os.remove("decrypted.jpg")  # Remove the decrypted image file

        wx.MessageBox('Image decompressed successfully!', 'Info', wx.OK | wx.ICON_INFORMATION)

    def show_image(self, filepath):
        # Show the image in a dialog
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(int(NewW), int(NewH))
        dialog = wx.Dialog(None)
        panel = wx.Panel(dialog)
        wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(img))
        dialog.ShowModal()

if __name__ == '__main__':
    app = PhotoCtrl()
    app.MainLoop()