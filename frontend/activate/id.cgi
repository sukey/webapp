#!/usr/bin/python
import urllib                                

def main():
    sock = urllib.urlopen("http://human.io/t/EoJr8vkzTDoYfBgGQ87ppfA18ZRL7EQsbw9cAEGt5Nk")
    htmlSource = sock.read()
    sock.close()
    idx1=htmlSource.find("<div id=\"shortcode\">")
    idx2=htmlSource.find("</div>",idx1)
    shortcode = htmlSource[idx1+20:idx2].strip()
    print "Content-type: text/html"
    print
    print shortcode

if __name__ == "__main__":
    main()
