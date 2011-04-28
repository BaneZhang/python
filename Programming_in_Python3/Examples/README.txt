Programming in Python 3
A Complete Introduction to the Python Language---second edition
by Mark Summerfield

ISBN: 978-0-13-712929-9

All the example programs and modules are copyright (c) Qtrac Ltd. 2008-9.
They are free software: you can redistribute them and/or modify them
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version version 3 of the License, or
(at your option) any later version. They are provided for educational
purposes and are distributed in the hope that they will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public Licenses (in file gpl-3.0.txt) for more details.

All the book's examples are designed to be educational, and many are
also designed to be useful. I hope that you find them helpful, and are
perhaps able to use some of them as starting points for your own
projects.

Most of the icons are from KDE (The `K' Desktop Environment), and come
under KDE's LGPL license. (Visit http:///www.kde.org for more information.)

Here is the list of programs referred to in the book grouped by chapter.
In addition the data and images subdirectories contain the sample data
and images that some of the programs use.

Note that these examples are for any Python 3.x version. (A separate set
of examples for Python 3.1 or later are available from
www.qtrac.eu/py3book.html.)

Chapter 1:
    average1_ans.py
    average2_ans.py
    awfulpoetry1_ans.py
    awfulpoetry2_ans.py
    bigdigits.py
    bigdigits_ans.py
    echoargs.py
    generate_grid.py
    hello.py
    sum1.py
    sum2.py
Chapter 2:
    csv2html.py
    csv2html1_ans.py
    csv2html2_ans.py
    print_unicode.py
    print_unicode_ans.py
    print_unicode_uni.py
    print_unicode_uni_ans.py
    quadratic.py
    quadratic_ans.py
    quadratic_uni.py
    quadratic_uni_ans.py
Chapter 3:
    external_sites.py
    external_sites_ans.py
    generate_test_names1.py
    generate_test_names2.py
    generate_usernames.py
    generate_usernames_ans.py
    grepword.py
    statistics.py
    uniquewords1.py
    uniquewords2.py
    uniquewords_ans.py
Chapter 4:
    checktags.py
    digit_names.py
    listkeeper.py
    make_html_skeleton.py
    noblanks.py
    TextUtil.py
    Util.py
Chapter 5:
    base64image.py
    capture.py
    CharGrid.py
    convert-incidents.py
    csv2html2_opt.py
    finddup.py
    Graphics/__init__.py
    Graphics/Bmp.py
    Graphics/Jpeg.py
    Graphics/Png.py
    Graphics/Tiff.py
    Graphics/Vector/__init__.py
    Graphics/Vector/Eps.py
    Graphics/Vector/Svg.py
    Graphics/Xpm.py
    ls.py
    untar.py
Chapter 6:
    Account.py
    Circle.py
    FuzzyBool.py
    FuzzyBoolAlt.py
    Image.py
    Image_ans.py
    Shape.py
    Shape_ans.py
    ShapeAlt.py
    ShapeAlt_ans.py
    SortedDict.py
    SortedList.py # See bug fix note at the end
Chapter 7:
    BikeStock.py
    BikeStock_ans.py
    BinaryRecordFile.py
    BinaryRecordFile_ans.py
    convert-incidents.py
    xdump.py
Chapter 8:
    Abstract.py
    Appliance.py
    Ascii.py
    Atomic.py
    Const.py
    ExternalStorage.py
    IndentedList.py
    magic-numbers.py
    magic-numbers_ans.py
    Meta.py
    Property.py
    SortedListAbc.py
    SortedListDelegate.py
    SortedListMeta.py
    SortKey.py
    TextFilter.py
    Valid.py
    XmlShadow.py
    find.py
Chapter 9:
    findduplicates-t.py
    findduplicates-t2.py # This has slightly improved logic over the version shown in the book
    findduplicates-m.py
    grepword-m.py
    grepword-p-child.py
    grepword-p.py
    grepword-p_ans.py
    grepword-t.py
    xmlsummary.py
Chapter 10:
    car_registration.py
    car_registration_ans.py
    car_registration_server.py
    car_registration_server_ans.py
Chapter 11:
    bookmarks.py
    dvds-dbm.py
    dvds-sql.py
Chapter 12:
    test_blocks.py
    test_Atomic.py
    test_Modules.py
Chapter 13:
    extract_tags.py
    html2text.py
    phone.py
Chapter 14:
    playlist.py (ReadKeyValue.py, ReadM3U.py)
    blocks.py (Block.py, BlockOutput.py)
    first-order-logic.py
    BibTeX.py
Chapter 15:
    bookmarks-tk.pyw
    bookmarks-tk_ans.pyw
    interest-tk.pyw
    regex-tk.pyw

NOTE: Util.py now has an improved equal_float() function with a slightly
different API. (An improved version of the old version is in the module
under the name equal_float_old().)

BUG FIX: Khan Fusion pointed out a subtle bug in the SortedList*.py
modules that caused incorrect behavior when the keys are strings and the
key function is
    lambda x: x.lower()
or
    lambda x: x.upper()
The bug has been fixed in all versions: however this means that the code
in the book is a bit different in places from that in this archive for
these modules. The fundamental algorithms used haven't changed, it is
just that the code now works correctly when there are multiple items
whose keys are the same even though their values are different.
(See the new doctests to see examples.)
