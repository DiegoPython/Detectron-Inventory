from simple_image_download import simple_image_download

sp = simple_image_download.Downloader()

keywords = ['apples', 'apple_gone_bad', 'banana', 'banana_gone_bad', 'pineapple', 'pineapple_gone_bad', 'carrot', 'carrot_gone_bad']

for keyword in keywords:
    print(f"Downloading pictures of: {keyword}")
    sp.download(keywords=keyword, limit=20)
