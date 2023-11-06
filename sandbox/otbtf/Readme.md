Changes made in :
1. helper.py - Added a function to get monoband image (flattened image).
2. otbtf_helper - Removed Patches extraction.

Steps on how to get the desired patches
1. Run otbtf_main.py - Doing everything except Patches_extraction
2. Change directory to remi_2 - This is a copy of remi_otbtf_keras_tutorial (You can find the whole tutorial in folder remi_test)
3. Run remi_patches_copy.py - Patches extraction is being done here.
    > 16*16*8 Patches : all/data/area2_0123_2023__A_xs_patches.tif, all/data/area2_0123_2023__B_xs_patches.tif
    > 16*16*1 Patches : all/data/area2_0123_2023__A_p_patches.tif, all/data/area2_0123_2023__B_p_patches.tif

4. Facing some issues in training with remi_test/training.py as well as our combined_model.py