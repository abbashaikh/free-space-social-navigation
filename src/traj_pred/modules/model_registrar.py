import os

import torch
import torch.nn as nn

class ModelRegistrar(nn.Module):
    """
    Class to register and manage multiple models in a dictionary
    """
    def __init__(self, model_dir, device):
        super(ModelRegistrar, self).__init__()
        self.model_dict = nn.ModuleDict()
        self.model_dir = model_dir
        self.device = device

    @staticmethod
    def get_model_device(model):
        """Returns the device of the model's parameters"""
        return next(model.parameters()).device

    def forward(self, *args, **kwargs):
        """Generic nn.Module forward method"""
        raise NotImplementedError(
            "Although ModelRegistrar is a nn.Module, it is only to store parameters."
        )

    def get_model(self, name, model_if_absent=None):
        """Returns the model dictionary
        4 cases: name in self.model_dict and model_if_absent is None         (OK)
                 name in self.model_dict and model_if_absent is not None     (OK)
                 name not in self.model_dict and model_if_absent is not None (OK)
                 name not in self.model_dict and model_if_absent is None     (NOT OK)
        """
        if name in self.model_dict:
            return self.model_dict[name]

        elif model_if_absent is not None:
            self.model_dict[name] = model_if_absent.to(self.device)
            return self.model_dict[name]

        else:
            raise ValueError(f"{name} was never initialized in this Registrar!")

    def get_name_match(self, name):
        """Retrieve models that match the given name"""
        ret_model_list = nn.ModuleList()
        for key in self.model_dict.keys():
            if name in key:
                ret_model_list.append(self.model_dict[key])
        return ret_model_list

    def get_all_but_name_match(self, name):
        """Retrieve models that do not match the given name"""
        ret_model_list = nn.ModuleList()
        for key in self.model_dict.keys():
            if name not in key:
                ret_model_list.append(self.model_dict[key])
        return ret_model_list

    def print_model_names(self):
        """Prints the names of all models in the model dictionary"""
        print(self.model_dict.keys())

    def save_models(self, curr_iter):
        """Saves the model dictionary to a file in the specified directory"""
        # Create the model directiory if it's not present.
        save_path = os.path.join(self.model_dir, f"model_registrar-{curr_iter}.pt")

        torch.save(self.model_dict, save_path)

    def load_models(self, iter_num):
        """Loads the model dictionary from a file in the specified directory"""
        self.model_dict.clear()

        save_path = os.path.join(self.model_dir, f"model_registrar-{iter_num}.pt")

        print("---------------------------------------")
        print("Loading from " + save_path)
        self.model_dict = torch.load(save_path, map_location=self.device)
        print("Loaded!")
        print("---------------------------------------")
