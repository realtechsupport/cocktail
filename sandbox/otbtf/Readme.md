Changes made in :
1. helper.py - Added a function to get monoband image (flattened image).
    > Right now we taking one band out of ther 8 - bands to check the model. But we either can take the average of bands or something different altogether
2. otbtf_helper - Removed Patches extraction.

Steps on how to get the desired patches
1. Run otbtf_main.py - Doing everything except Patches_extraction
2. Change directory to remi_2 - This is a copy of remi_otbtf_keras_tutorial (You can find the whole tutorial in folder remi_test)
3. Run remi_patches_copy.py - Patches extraction is being done here.
    > 16*16*8 Patches : all/data/area2_0123_2023__A_xs_patches.tif, all/data/area2_0123_2023__B_xs_patches.tif
    > 16*16*1 Patches : all/data/area2_0123_2023__A_p_patches.tif, all/data/area2_0123_2023__B_p_patches.tif

4. Facing some issues in training with remi_test/training.py as well as our combined_model.py


Why the changes are made:
--------------------------------------------------------------------------------
The issue that we were facing because patches extraction, make patches according to the band
If input is 8 bands - patches will be 8 bands (16*16*8)
** If input will be monoband - patches will be monoband : This is effectively mask image. (16*16*1)
However, we are still keeping labels as ouput, because it is being used in the pipeline ahead. (1*1*1)

Since remi is using all three patches of the same shape, We are also keeping all three patches.