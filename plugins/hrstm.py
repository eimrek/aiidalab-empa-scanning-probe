
from aiida.orm.calculation.job import JobCalculation
from aiida.common.utils import classproperty
from aiida.orm.data.structure import StructureData
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.singlefile import SinglefileData
from aiida.orm.data.remote import RemoteData
from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.common.exceptions import InputValidationError


class HrstmCalculation(JobCalculation):

    # --------------------------------------------------------------------------
    def _init_internal_params(self):
        """
        Set parameters of instance
        """
        super(HrstmCalculation, self)._init_internal_params()

    # --------------------------------------------------------------------------
    @classproperty
    def _use_methods(cls):
        """
        Extend the parent _use_methods with further keys.
        This will be manually added to the _use_methods in each subclass
        """
        retdict = JobCalculation._use_methods
        retdict.update({
            "parameters": {
               'valid_types': ParameterData,
               'additional_parameter': None,
               'linkname': 'parameters',
               'docstring': "The node that specifies the "
                            "input parameters",
               },
            "parent_calc_folder": {
               'valid_types': RemoteData,
               'additional_parameter': None,
               'linkname': 'parent_calc_folder',
               'docstring': "Use a remote folder as parent folder ",
               },
            "ppm_cal_folder": {
               'valid_types': RemoteData,
               'additional_parameter': None,
               'linkname': 'ppm_calc_folder',
               'docstring': "Use a remote folder as ppm folder ",
              },
#            "settings": {
#               'valid_types': ParameterData,
#               'additional_parameter': None,
#               'linkname': 'settings',
#               'docstring': "Special settings",
#               },
            })
        return retdict

    # --------------------------------------------------------------------------
    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        This is the routine to be called when you want to create
        the input files and related stuff with a plugin.
        :param tempfolder: a aiida.common.folders.Folder subclass where
                           the plugin should put all its files.
        :param inputdict: a dictionary with the input nodes, as they would
                be returned by get_inputdata_dict (without the Code!)
        """

        ### ------------------------------------------------------
        ###  Input check
        try:
            parameters = inputdict.pop(self.get_linkname('parameters'))
        except KeyError:
            raise InputValidationError("No parameters specified for this calculation")
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters is not of type ParameterData")

        try:
            code = inputdict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("No code specified for this calculation")

        try:
            parent_calc_folder = inputdict.pop(self.get_linkname('parent_calc_folder'))
        except KeyError:
            raise InputValidationError("No parent_calc_folder specified for this calculation")
        if not isinstance(parent_calc_folder, RemoteData):
            raise InputValidationError("parent_calc_folder is not of type RemoteData")

        try:
            ppm_calc_folder = inputdict.pop(self.get_linkname('ppm_calc_folder'))
        except KeyError:
            raise InputValidationError("No ppm_calc_folder specified for this calculation")
        if not isinstance(ppm_calc_folder, RemoteData):
            raise InputValidationError("ppm_calc_folder is not of type RemoteData")

        try:
            settings = inputdict.pop(self.get_linkname('settings'))
        except KeyError:
            raise InputValidationError("No settings specified for this calculation")
        if not isinstance(settings, ParameterData):
            raise InputValidationError("settings is not of type ParameterData")
        settings_dict = settings.get_dict()

        # Here, there should be no more parameters...
        if inputdict:
            raise InputValidationError("The following input data nodes are "
                "unrecognized: {}".format(inputdict.keys()))

        ###  End of input check
        ### ------------------------------------------------------

        # create calc info
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.cmdline_params = codeinfo.cmdline_params
        calcinfo.codes_info = [codeinfo]

        # file lists
        calcinfo.remote_symlink_list = []
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []

        calcinfo.retrieve_list = settings_dict.pop('additional_retrieve_list', [])

        cmdline = []
        for key in parameters.dict:
            if key == 'rotate':
                if parameters.dict[key]:
                    cmdline += '--rotate'
            else:
                cmdline += [key]
                if parameters.dict[key] != '':
                    cmdline += parameters.dict[key]

        codeinfo.cmdline_params = cmdline

        # symlinks
        if parent_calc_folder is not None:
            comp_uuid = parent_calc_folder.get_computer().uuid
            remote_path = parent_calc_folder.get_remote_path()
            symlink = (comp_uuid, remote_path, self._PARENT_CALC_FOLDER_NAME)
            calcinfo.remote_symlink_list.append(symlink)
        if ppm_cal_folder is not None:
            comp_uuid = ppm_calc_folder.get_computer().uuid
            remote_path = ppm_calc_folder.get_remote_path()
            symlink = (comp_uuid, remote_path, self._PPM_CALC_FOLDER_NAME)
            calcinfo.remote_symlink_list.append(symlink)


        return calcinfo

# EOF
