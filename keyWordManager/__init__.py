from krita import DockWidgetFactory, DockWidgetFactoryBase
from .docker_template import DockerTemplate

DOCKER_ID = 'keyWordManager'
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                                        DockWidgetFactoryBase.DockRight,
                                        DockerTemplate)

instance.addDockWidgetFactory(dock_widget_factory)