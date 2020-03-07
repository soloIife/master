"""
xml parse
"""


class Element:
    def __init__(self, name, properties=None, content=None, parent=None):
        self._content = content
        self.name = name
        self.properties = properties
        self.__child_list = []
        self.is_root = False
        self.parent = parent

    def __hash__(self):
        return id(self)

    def add_child(self, el):
        self.__child_list.append(el)

    def __iter__(self):
        return iter(self.__child_list)

    def __getitem__(self, item):
        return self.__child_list[item]

    def get_attr(self, k):
        if k not in self.properties:
            raise Exception("no that properties")
        return self.properties[k]

    def get_element_by_id(self, id):
        if id == self.properties.get("id"):
            return self

        for e in self.__child_list:
            t = e.get_element_by_id(id)
            if t is not None:
                return t

    def get_element_by_property(self, attr, value):
        res = []
        if value == self.properties.get(attr):
            res.append(self)
        for e in self.__child_list:
            t = e.get_element_by_property(attr, value)
            res.extend(t)
        return res

    def get_elements_by_tag_name(self, tag_name):
        res = []
        if tag_name == self.name:
            res.append(self)
        for e in self.__child_list:
            t = e.get_elements_by_tag_name(tag_name)
            res.extend(t)
        return res

    def set_attr(self, k, v):
        self.properties[k] = v

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, text):
        self._content = text

    def to_xml(self, n=0):
        prop = []
        for k, v in self.properties.items():
            prop.append('%s="%s"' % (k, v))
        prop = " ".join(prop)
        if len(prop) != 0:
            prop = " %s " % prop
        if self._content is None:
            text = "{s}<{tag}{prop}/>".format(s=" "*n,tag=self.name, prop=prop)
        else:
            head = "{s}<{tag}{prop}>".format(s=" "*n,tag=self.name, prop=prop)
            if self.__child_list:
                ts = []
                for e in self.__child_list:
                    ct: str = e.to_xml(2)
                    ts.append("%s%s" % (" "*n, ct))
                content = "\n".join(ts)
                space = "\n"
                tail = "%s</%s>" % (" " * n, self.name)
            else:
                content = self._content
                space = ""
                tail = "</%s>" % self.name
            text = "{head}{space}{content}{space}{tail}".format(head=head, space=space, content=content, tail=tail)
        return text

    @property
    def child_nodes(self):
        return self.__child_list

    def __repr__(self):
        return self.name

    __str__ = __repr__


def correspond_tag(info_list, tag, start, i):
    for info in reversed(info_list):
        if info[0] == tag and info[-1] is None:
            info[-1] = i
            info[-2] = start
            return


def parse(text: str):
    i = 0
    elements = []
    while i < len(text):
        s = text[i]
        if s == "<":
            start = i
        elif s == ">":
            tag = text[start + 1:i]
            if tag[0] == "/":
                tag = tag[1:].split()[0]
                correspond_tag(elements, tag, start, i)
            elif tag[-1] == "/":
                tag = tag[:-1].split()[0]
                elements.append([tag, start, i, None, None])
                correspond_tag(elements, tag, None, i)
            else:
                tag = tag.split()[0]
                elements.append([tag, start, i, None, None])
        i += 1
    node_list = []
    node_info_map = {}
    for i in range(len(elements)):
        t = elements[i]
        head = text[t[1]:t[2] + 1]
        head = head.strip("</>")
        ls = head.split()
        tag_name = ls[0]
        properties = {}
        for arg in ls:
            if "=" in arg:
                kv = arg.split("=")
                properties[kv[0]] = kv[1].strip('\'"')
        if t[2] == t[-1]:
            content = None
        else:
            content = text[t[2] + 1:t[-2]]
            if "<" in content:
                content = 0
        node = Element(tag_name, properties, content)
        node_list.append((t[1], t[-1], node))
        node_info_map[node] = (t[1], t[-1])
    old_s, old_e, old_node = node_list[0]
    parent = old_node
    ps, pe = old_s, old_e
    parent.is_root = True
    for start, end, node in node_list[1:]:
        if old_s < start and end < old_e:
            parent = old_node
            ps, pe = old_s, old_e
            node.parent = parent
            parent.add_child(node)
        else:
            while 1:
                if ps < start < pe:
                    node.parent = parent
                    parent.add_child(node)
                    break
                if parent is None:
                    break
                parent = parent.parent
                ps, pe = node_info_map[parent]
        old_s = start
        old_e = end
        old_node = node
    root = node_list[0][2]
    return root
