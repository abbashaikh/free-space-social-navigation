import numpy as np


def prediction_output_to_trajectories(
    prediction_output_dict, dt, max_h, ph, map=None, prune_ph_to_future=False
):

    prediction_timesteps = prediction_output_dict.keys()

    output_dict = dict()
    histories_dict = dict()
    futures_dict = dict()

    for t in prediction_timesteps:
        histories_dict[t] = dict()
        output_dict[t] = dict()
        futures_dict[t] = dict()
        prediction_nodes = prediction_output_dict[t].keys()
        for node in prediction_nodes:
            predictions_output = prediction_output_dict[t][node]
            position_state = {"position": ["x", "y"]}

            history = node.get(
                np.array([t - max_h, t]), position_state
            )  # History includes current pos
            history = history[~np.isnan(history.sum(axis=1))]

            future = node.get(np.array([t + 1, t + ph]), position_state)
            future = future[~np.isnan(future.sum(axis=1))]

            if prune_ph_to_future:
                predictions_output = predictions_output[:, :, : future.shape[0]]
                if predictions_output.shape[2] == 0:
                    continue

            trajectory = predictions_output

            if map is None:
                histories_dict[t][node] = history
                output_dict[t][node] = trajectory
                futures_dict[t][node] = future
            else:
                histories_dict[t][node] = map.to_map_points(history)
                output_dict[t][node] = map.to_map_points(trajectory)
                futures_dict[t][node] = map.to_map_points(future)

    return output_dict, histories_dict, futures_dict

def convert_to_world_tf(prediction_output_dict, obs, idx):
    current_state = obs.curr_agent_state[idx, :2].cpu().numpy()
    agent_to_world_tf = obs.agents_from_world_tf[idx, :2, :2].cpu().numpy()
    agent_name = obs.agent_name[idx]

    history_st = obs.agent_hist[idx, :, :2].cpu().numpy()
    history_st = history_st[~np.isnan(history_st.sum(axis=1))]
    history = history_st @ agent_to_world_tf + current_state

    future_st = obs.agent_fut[idx, :, :2].cpu().numpy()
    future_st = future_st[~np.isnan(future_st.sum(axis=1))]
    future = future_st @ agent_to_world_tf + current_state

    prediction = prediction_output_dict[agent_name] @ agent_to_world_tf + current_state

    return history, future, prediction