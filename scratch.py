#!/usr/bin/env python
import npr


if __name__ == '__main__':
    p = npr.Player()
    while True:
       status = p.play()
       status.wait()

