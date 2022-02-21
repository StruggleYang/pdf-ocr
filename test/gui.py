#!/usr/bin/python

import wx

class FicheFrame( wx.Frame ) :

    def __init__( self ) :

        wx.Frame.__init__( self, None,-1, "FicheFrame", size=(300, 400) )

        scrollWin = wx.PyScrolledWindow( self, -1 )

        stTxt = wx.StaticText(scrollWin, -1, "txtStr", pos=(20, 20))

        for i in range( 50 ) :
            stTxt.SetLabel('%s%s%d\n' % (stTxt.GetLabel(),'txtStr',i))

        w, h = stTxt.GetSize()
        print(w, h)

        #end for

        scrollWin.SetScrollbars( 0, 1,  0, h+10 )
        scrollWin.SetScrollRate( 1, 1 )      # Pixels per scroll increment

    #end __init__ def

#end class

if __name__ == '__main__' :

    myapp = wx.App( redirect=False )

    myAppFrame = FicheFrame()
    myAppFrame.Show()

    myapp.MainLoop()