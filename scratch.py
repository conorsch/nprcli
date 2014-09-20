import npr
#s = npr.show.Show()


if __name__ == '__main__':
    p = npr.Player()
    while True:
       status = p.play()
       status.wait()
