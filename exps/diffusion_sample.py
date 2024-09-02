import os

import torch

from tools.dataloader import get_loaders
from models.autoencoder.autoencoder_spade import ViTAutoencoder_SPADE
from models.ddpm.unet_mask_3d import UNetModel, DiffusionWrapper
from evals.eval_cond import save_image_ddpm_mask

import copy
from utils import file_name, Logger

#----------------------------------------------------------------------------

_num_moments    = 3             # [num_scalars, sum_of_scalars, sum_of_squares]
_reduce_dtype   = torch.float32 # Data type to use for initial per-tensor reduction.
_counter_dtype  = torch.float64 # Data type to use for the internal counters.
_rank           = 0             # Rank of the current process.
_sync_device    = None          # Device to use for multiprocess communication. None = single-process.
_sync_called    = False         # Has _sync() been called yet?
_counters       = dict()        # Running counters on each device, updated by report(): name => device => torch.Tensor
_cumulative     = dict()        # Cumulative counters on the CPU, updated by _sync(): name => torch.Tensor
_ema_ckpt_num = 29500

def diffusion_sample(rank, args):
    device = torch.device('cuda', rank)

    """ ROOT DIRECTORY """
    fn = file_name(args)
    logger = Logger(fn, ask=False)
    logger.log(args)
    logger.log(f'Log path: {logger.logdir}')
    rootdir = logger.logdir

    if logger is None:
        log_ = print
    else:
        log_ = logger.log

    """ Get Image """
    log_(f"Loading dataset {args.data} with resolution {args.res}")
    train_loader, test_loader, total_vid = get_loaders(rank, args.data, args.res, args.timesteps, args.skip, args.batch_size, args.n_gpus, args.seed, args.cond_model)

    """ Get Model """
    log_(f"Generating model")

    torch.cuda.set_device(rank)
    first_stage_model_src = ViTAutoencoder_SPADE(embed_dim=16, ch_mult=(1,2,4,8)).to(device)
    first_stage_model_trg = ViTAutoencoder_SPADE(embed_dim=16, ch_mult=(1,2,4,8)).to(device)

    first_stage_model_src_ckpt = torch.load(args.first_model_src, map_location='cuda:2')
    first_stage_model_trg_ckpt = torch.load(args.first_model_trg, map_location='cuda:2')
    first_stage_model_src.load_state_dict(first_stage_model_src_ckpt)
    first_stage_model_trg.load_state_dict(first_stage_model_trg_ckpt)
    del first_stage_model_src_ckpt
    del first_stage_model_trg_ckpt
    print('First stage model loaded')

    unet = UNetModel(**args.unetconfig)
    model = DiffusionWrapper(unet).to(device)

    if os.path.exists(rootdir + f'model_' + str(_ema_ckpt_num) + '.pth'):
        model_ckpt = torch.load(rootdir + f'model_' + str(_ema_ckpt_num) + '.pth', map_location='cuda:2')
        model.load_state_dict(model_ckpt)
        ema_model = copy.deepcopy(model)
        print('Diffusion model loaded')

        del model_ckpt

    else:
        raise FileNotFoundError("Diffusion model cannot be loaded")

    first_stage_model_src.eval()
    first_stage_model_trg.eval()
    ema_model.eval()

    save_image_ddpm_mask(rank, ema_model, first_stage_model_src, first_stage_model_trg, _ema_ckpt_num, test_loader, logger)

