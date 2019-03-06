import Orange
from Orange.widgets.tests.base import WidgetTest
from orangecontrib.spectroscopy.tests.spectral_preprocess import pack_editor
from orangecontrib.spectroscopy.widgets.owintegrate import OWIntegrate, PREPROCESSORS,\
    IntegrateSimpleEditor
from orangecontrib.spectroscopy.tests import spectral_preprocess


class TestOWIntegrate(WidgetTest):

    def setUp(self):
        self.widget = self.create_widget(OWIntegrate)

    def test_load_unload(self):
        self.send_signal("Data", Orange.data.Table("iris.tab"))
        self.send_signal("Data", None)

    def test_allint_indv(self):
        data = Orange.data.Table("peach_juice.dpt")
        for p in PREPROCESSORS:
            self.widget = self.create_widget(OWIntegrate)
            self.send_signal("Data", data)
            self.widget.add_preprocessor(p)
            # direct calls the preview so that exceptions do not get lost in Qt
            self.widget.show_preview()
            self.widget.apply()

    def test_allint_indv_empty(self):
        data = Orange.data.Table("peach_juice.dpt")[:0]
        for p in PREPROCESSORS:
            self.widget = self.create_widget(OWIntegrate)
            self.send_signal("Data", data)
            self.widget.add_preprocessor(p)
            self.widget.show_preview()  # direct call
            self.widget.apply()
        # no attributes
        data = Orange.data.Table("peach_juice.dpt")
        data = Orange.data.Table(
            Orange.data.Domain([],
                               class_vars=data.domain.class_vars,
                               metas=data.domain.metas),
            data)
        for p in PREPROCESSORS:
            self.widget = self.create_widget(OWIntegrate)
            self.send_signal("Data", data)
            self.widget.add_preprocessor(p)
            self.widget.show_preview()  # direct call
            self.widget.apply()

    def test_saving_preview_position(self):
        self.send_signal("Data", Orange.data.Table("iris.tab"))
        self.widget.add_preprocessor(self.widget.PREPROCESSORS[0])
        self.widget.add_preprocessor(self.widget.PREPROCESSORS[0])
        settings = self.widget.settingsHandler.pack_data(self.widget)
        self.widget = self.create_widget(OWIntegrate, stored_settings=settings)
        self.assertEqual([], self.widget.preview_n)
        self.widget.flow_view.set_preview_n(1)
        settings = self.widget.settingsHandler.pack_data(self.widget)
        self.widget = self.create_widget(OWIntegrate, stored_settings=settings)
        settings = self.widget.settingsHandler.pack_data(self.widget)
        self.assertEqual([1], settings["preview_n"])
        self.widget.flow_view.set_preview_n(None)
        settings = self.widget.settingsHandler.pack_data(self.widget)
        self.widget = self.create_widget(OWIntegrate, stored_settings=settings)
        self.assertEqual([], self.widget.preview_n)

    def test_output_as_metas(self):
        data = Orange.data.Table("iris.tab")
        self.widget.output_metas = True
        self.send_signal(OWIntegrate.Inputs.data, data)
        self.widget.add_preprocessor(self.widget.PREPROCESSORS[0])
        self.widget.apply()
        out_data = self.get_output(OWIntegrate.Outputs.preprocessed_data)
        self.assertEqual(len(data.domain.attributes), len(out_data.domain.attributes))
        self.assertEqual(1, len(out_data.domain.metas))
        preprocessor = self.get_output(OWIntegrate.Outputs.preprocessor)
        preprocessed = preprocessor(data)
        self.assertEqual(len(data.domain.attributes), len(preprocessed.domain.attributes))
        self.assertEqual(1, len(out_data.domain.metas))

    def test_output_as_non_metas(self):
        self.widget.output_metas = False
        data = Orange.data.Table("iris.tab")
        self.send_signal(OWIntegrate.Inputs.data, data)
        self.widget.add_preprocessor(self.widget.PREPROCESSORS[0])
        self.widget.apply()
        out_data = self.get_output(OWIntegrate.Outputs.preprocessed_data)
        self.assertEqual(1, len(out_data.domain.attributes))
        self.assertEqual(0, len(out_data.domain.metas))
        preprocessor = self.get_output(OWIntegrate.Outputs.preprocessor)
        out_data = preprocessor(data)
        preprocessed = preprocessor(data)
        self.assertEqual(1, len(preprocessed.domain.attributes))
        self.assertEqual(0, len(out_data.domain.metas))

    def test_simple_preview(self):
        data = Orange.data.Table("iris.tab")
        self.send_signal(OWIntegrate.Inputs.data, data)
        self.widget.add_preprocessor(pack_editor(IntegrateSimpleEditor))
        self.widget.show_preview()
        self.assertEqual(0, len(self.widget.curveplot.markings))
        self.widget.flow_view.set_preview_n(0)
        self.widget.show_preview()
        self.assertGreater(len(self.widget.curveplot.markings), 0)


class TestIntegrateWarning(spectral_preprocess.TestWarning):
    widget_cls = OWIntegrate
