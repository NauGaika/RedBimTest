class Precast_panel_join(object):

    def join_units_to_panel(self):
        for i in self.units:
            self.join_elements([self], i.subcomponents)