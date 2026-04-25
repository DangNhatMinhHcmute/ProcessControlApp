import json
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.exporter.variants import pnml as pnml_exporter
from pm4py.objects.petri_net.importer.variants import pnml as pnml_importer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from PIL import Image, ImageTk
import tempfile
import os

class PetriNetBuilder:
    def __init__(self, name="CustomPetriNet"):
        self.net = PetriNet(name)
        self.places = {}
        self.transitions = {}
        self.initial_marking = Marking()
        self.final_marking = Marking()

    def add_place(self, name):
        place = PetriNet.Place(name)
        self.net.places.add(place)
        self.places[name] = place

    def add_transition(self, name, vitural_transition=False):
        if vitural_transition == True:
            label = None
        else:
            label = name
        if name in self.transitions:
            raise ValueError(f"Transition with name '{name}' already exists.")
        transition = PetriNet.Transition(name, label)
        self.net.transitions.add(transition)
        self.transitions[name] = transition

    def add_arc(self, source_name, target_name):
        source = self.places.get(source_name) or self.transitions.get(source_name)
        target = self.places.get(target_name) or self.transitions.get(target_name)
        if source and target:
            arc = PetriNet.Arc(source, target)
            self.net.arcs.add(arc)
            source.out_arcs.add(arc)
            target.in_arcs.add(arc)
        else:
            raise ValueError("Invalid source or target for arc")

    def remove_arc(self, source_name, target_name):
        for arc in list(self.net.arcs):
            if arc.source.name == source_name and arc.target.name == target_name:
                arc.source.out_arcs.remove(arc)
                arc.target.in_arcs.remove(arc)
                self.net.arcs.remove(arc)
                break

    def remove_transition(self, name):
        transition = self.transitions.get(name)
        if transition:
            # Xác định places đầu vào và đầu ra
            input_places = set(arc.source for arc in transition.in_arcs if isinstance(arc.source, PetriNet.Place))
            output_places = set(arc.target for arc in transition.out_arcs if isinstance(arc.target, PetriNet.Place))

            # Xóa các arc liên quan
            for arc in list(self.net.arcs):
                if arc.source == transition or arc.target == transition:
                    arc.source.out_arcs.discard(arc)
                    arc.target.in_arcs.discard(arc)
                    self.net.arcs.remove(arc)

            # Xóa transition khỏi net và danh sách
            self.net.transitions.remove(transition)
            del self.transitions[name]
            # Xóa các places đầu vào và đầu ra nếu không còn arc nào khác
            for place in input_places.union(output_places): 
                if not place.out_arcs and not place.in_arcs:
                    self.net.places.remove(place)
                    del self.places[place.name]
    def remove_place(self, name):
        place = self.places.get(name)
        if place:
            # Xóa các cung liên quan
            for arc in list(self.net.arcs):
                if arc.source == place or arc.target == place:
                    arc.source.out_arcs.discard(arc)
                    arc.target.in_arcs.discard(arc)
                    self.net.arcs.remove(arc)

            # Xóa khỏi marking nếu có
            self.initial_marking.pop(place, None)
            self.final_marking.pop(place, None)

            # Xóa khỏi net và danh sách theo tên
            self.net.places.remove(place)
            del self.places[name]
            
    def rename_transition(self, old_name, new_name):
        transition = self.transitions.get(old_name)
        if transition:
            transition.name = new_name
            transition.label = new_name
            self.transitions[new_name] = transition
            del self.transitions[old_name]

    def set_initial_marking(self, place_name, tokens=1):
        place = self.places.get(place_name)
        if place:
            self.initial_marking[place] = tokens

    def set_final_marking(self, place_name, tokens=1):
        place = self.places.get(place_name)
        if place:
            self.final_marking[place] = tokens

    def get_petri_net(self):
        return self.net, self.initial_marking, self.final_marking

    def save_to_json(self, filepath):
        data = {
            "places": list(self.places.keys()),
            "transitions": {t.name: t.label for t in self.transitions.values()},
            "arcs": [(arc.source.name, arc.target.name) for arc in self.net.arcs],
            "initial_marking": {p.name: t for p, t in self.initial_marking.items()},
            "final_marking": {p.name: t for p, t in self.final_marking.items()}
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.__init__(self.net.name)

        for p in data["places"]:
            self.add_place(p)

        for t_name, label in data["transitions"].items():
            self.add_transition(t_name, label)

        for src, tgt in data["arcs"]:
            self.add_arc(src, tgt)

        for p, t in data["initial_marking"].items():
            self.set_initial_marking(p, t)

        for p, t in data["final_marking"].items():
            self.set_final_marking(p, t)
    
    def save_to_pnml(self, filepath):
        pnml_exporter.export_net(self.net, self.initial_marking, filepath)
    
    def load_from_pnml(self, filepath):
        self.net, self.initial_marking, self.final_marking = pnml_importer.import_net(filepath)

        # Làm mới danh sách place và transition theo tên
        self.places = {p.name: p for p in self.net.places}
        self.transitions = {t.name: t for t in self.net.transitions}
        
    def from_existing_net(self, net, initial_marking, final_marking):
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.places = {p.name: p for p in net.places}
        self.transitions = {t.name: t for t in net.transitions}
        
def render_to_tk_image(model_type: str, rankdir: str,net = None, initial_marking = None, final_marking = None):
    # Vẽ model bằng Graphviz
    if model_type == "Petri Net":
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    elif model_type == "BPMN":
        gviz = bpmn_visualizer.apply(net)
        
    gviz.attr(
        rankdir=rankdir
    )
    # Tạo tệp tạm thời để lưu hình ảnh
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        pn_visualizer.save(gviz, tmp_file_path)

    # Đọc hình ảnh từ tệp tạm thời
    image = Image.open(tmp_file_path)
    image.thumbnail((image.width // 3*2, image.height // 3*2), Image.LANCZOS)

    # Chuyển đổi sang định dạng Tkinter
    tk_image = ImageTk.PhotoImage(image)

    # Xóa tệp tạm thời
    os.remove(tmp_file_path)

    return tk_image
