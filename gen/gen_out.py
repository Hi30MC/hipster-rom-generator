import nbtlib
from nbtlib import File, schema
from nbtlib.tag import *
from gen.gen_util import *

# gen file base
out = gen_base()

# add entity list to file
out.update({
    "Entities": List([
        gen_cart(items=[
            gen_ss_sb(0, 1),
            gen_ss_sb(1, 9),
            gen_ss_disc(2, 8),
            gen_ss_disc(3, 4)
        ])
    ])
})

# save file
out.save("output_schematics/test/test3.schem")