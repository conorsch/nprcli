import npr.show
#s = npr.show.Show()

if __name__ == '__main__':
    p = npr.show.Player()
    while True:
       status = p.play()
       status.wait()
