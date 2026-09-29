import cv2                                                                                                     
img = cv2.imread('rapport/QR code.png')                                                  
print(cv2.QRCodeDetector().detectAndDecode(img)[0]) 