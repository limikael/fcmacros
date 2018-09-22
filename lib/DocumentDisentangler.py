import FreeCAD, os, RaytracingGui, shutil, Mesh, MeshPart, FreeCADGui, time

class DupShape:
	def __init__(self, obj, dupShape):
		obj.Proxy=self
		self.dupShape=dupShape

	def execute(self, fp):
		fp.Shape=self.dupShape

class ViewProviderDupShape:
	def __init__(self, obj):
		obj.Proxy=self

	def getDefaultDisplayMode(self):
		return "Default"

class DocumentDisentangler:
	def __init__(self):
		pass

	def __getDocumentByFileName(self, fileName):
		docList=FreeCAD.listDocuments()
		for docName in docList:
			doc=FreeCAD.getDocument(docName)
			if doc.FileName==fileName:
				return doc

		doc=FreeCAD.openDocument(fileName)
		self.__tmpDocs.append(doc.Name)
		return doc

	def __processObjects(self, objs, matrix=None, processInvisible=False, processPartChildren=False):
		if matrix is None:
			matrix=FreeCAD.Matrix()

		for obj in objs:
			process=True

			if not processPartChildren:
				for parent in obj.InList:
					if parent.TypeId=="App::Part":
						process=False

			if not processInvisible:
				if not obj.ViewObject.isVisible():
					process=False

#			if processInvisible or obj.ViewObject.isVisible():
			if process:
				if obj.TypeId=="Part::Compound":
					m=matrix.multiply(obj.Placement.toMatrix())
					self.__processObjects(obj.OutList,m,True)

				elif obj.TypeId=="Part::FeaturePython" \
						and hasattr(obj,"sourceFile"):
					m=matrix.multiply(obj.Placement.toMatrix())
					other=self.__getDocumentByFileName(obj.sourceFile)
					self.__processObjects(other.Objects,m)

				elif obj.TypeId.split("::")[0] in ["Part","PartDesign"]:
					o=self.__target.addObject("Part::FeaturePython",obj.Label)
					DupShape(o,obj.Shape)
					ViewProviderDupShape(o.ViewObject)
					o.ViewObject.ShapeColor=obj.ViewObject.ShapeColor
					o.Placement=FreeCAD.Placement(matrix.multiply(obj.Placement.toMatrix()))

				elif obj.TypeId.split("::")[0]=="Mesh":
					o=self.__target.addObject("Mesh::Feature")
					o.Mesh=obj.Mesh
					o.ViewObject.ShapeColor=obj.ViewObject.ShapeColor

				elif obj.TypeId=="App::Part":
					m=matrix.multiply(obj.Placement.toMatrix())
					self.__processObjects(obj.Group,m,processPartChildren=True)

	def disentangle(self, doc=None):
		start=time.time()

		self.__tmpDocs=[]

		if doc is None:
			doc=FreeCAD.activeDocument()

		self.__doc=doc
		self.__target=FreeCAD.newDocument()

		self.__processObjects(self.__doc.Objects)

		docView=FreeCADGui.getDocument(self.__doc.Name)
		targetView=FreeCADGui.getDocument(self.__target.Name)
		targetView.ActiveView.setCamera(docView.ActiveView.getCamera())

		self.__target.recompute()

		for tmpDoc in self.__tmpDocs:
			FreeCAD.closeDocument(tmpDoc)

		print "Disentangle took: "+str(time.time()-start)
		return self.__target