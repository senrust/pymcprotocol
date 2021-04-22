from pymcprotocol import Type3E

def test_type3e():
    pyplc = Type3E()
    pyplc.connect("192.168.1.203", 1025)
    # check batch access to word units
    pyplc.batchwrite_wordunits("D1000", [0, 1000, -1000])
    value = pyplc.batchread_wordunits("D1000", 3)
    assert [0, 1000, -1000] == value

    # check batch access to bit units
    # odd size test
    pyplc.batchwrite_bitunits("M10", [0, 1, 1])
    value = pyplc.batchread_bitunits("M10", 3)
    assert [0, 1, 1] == value
    #even size test
    pyplc.batchwrite_bitunits("M20", [1, 0, 1, 0])
    value = pyplc.batchread_bitunits("M20", 4)
    assert  [1, 0, 1, 0] == value
    #test word access
    pyplc.batchwrite_bitunits("M30", [1, 1, 1, 1])
    value = pyplc.batchread_wordunits("M30", 1)
    assert 15 == value

    # test random access
    pyplc.randomwrite(["D2000", "D2010", "D2020"], [-10, 0, 10], ["D2040", "D2050", "D2060", "D2070", "D2080"], [-10000000, -1, 0, 1, 10000000])
    word_values, dword_values = pyplc.randomread(["D2000", "D2010", "D2020"], ["D2040", "D2050", "D2060", "D2070", "D2080"])
    assert word_values == [-10, 0, 10]
    assert dword_values == [-10000000, -1, 0, 1, 10000000]

    #test random bit access
    pyplc.randomwrite_bitunits(["M40", "M45", "M50", "M60"], [1, 1, 1, 1])
    word_values, dword_values = pyplc.randomread(["M40"], ["M40"])
    assert word_values == [1057]
    assert dword_values == [1049633]