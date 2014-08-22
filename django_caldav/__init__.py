__author__ = 'Petr Knap <knap@wpj.cz>'


def print_xml(xml_as_string):
    if xml_as_string:
        from xml.dom import minidom
        xml_as_dom = minidom.parseString(xml_as_string)
        print xml_as_dom.toprettyxml()