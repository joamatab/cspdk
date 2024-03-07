from __future__ import annotations

from functools import cache, partial

import jax
import jax.numpy as jnp
import sax
from gplugins.sax.models import bend, coupler, grating_coupler, straight

from cspdk.tech import LAYER

nm = 1e-3

################
# PassThrus
################


@cache
def _2port(p1, p2):
    @jax.jit
    def _2port(wl=1.5):
        wl = jnp.asarray(wl)
        return sax.reciprocal({(p1, p2): jnp.ones_like(wl)})

    return _2port


@cache
def _3port(p1, p2, p3):
    @jax.jit
    def _3port(wl=1.5):
        wl = jnp.asarray(wl)
        thru = jnp.ones_like(wl) / jnp.sqrt(2)
        return sax.reciprocal(
            {
                (p1, p2): thru,
                (p1, p3): thru,
            }
        )

    return _3port


@cache
def _4port(p1, p2, p3, p4):
    @jax.jit
    def _4port(wl=1.5):
        wl = jnp.asarray(wl)
        thru = jnp.ones_like(wl) / jnp.sqrt(2)
        cross = 1j * thru
        return sax.reciprocal(
            {
                (p1, p4): thru,
                (p2, p3): thru,
                (p1, p3): cross,
                (p2, p4): cross,
            }
        )

    return _4port


################
# Waveguides
################

straight_sc = partial(straight, wl0=1.55, neff=2.4, ng=4.2)
straight_so = partial(straight, wl0=1.31, neff=2.4, ng=4.2)
straight_rc = partial(straight, wl0=1.55, neff=2.4, ng=4.2)
straight_ro = partial(straight, wl0=1.31, neff=2.4, ng=4.2)
straight_nc = partial(straight, wl0=1.55, neff=2.4, ng=4.2)
straight_no = partial(straight, wl0=1.31, neff=2.4, ng=4.2)


def _layer_eq(layer1, layer2):
    return (int(layer1[0]) == int(layer2[0])) and (int(layer1[1]) == int(layer2[1]))


def _check_cross_section(cross_section):
    if isinstance(cross_section, str):
        return cross_section
    err = ValueError(f"Unknown cross section {cross_section}")
    if _layer_eq(cross_section["sections"][0]["layer"], LAYER.WG):
        if len(cross_section["sections"]) > 1:
            if cross_section["sections"][0]["width"] == 0.45:
                return "xs_rc"
            elif cross_section["sections"][0]["width"] == 0.40:
                return "xs_ro"
            else:
                raise err
        elif cross_section["sections"][0]["width"] == 0.45:
            return "xs_sc"
        elif cross_section["sections"][0]["width"] == 0.40:
            return "xs_so"
        else:
            raise err
    elif _layer_eq(cross_section["sections"][0]["layer"], LAYER.NITRIDE):
        if cross_section["sections"][0]["width"] == 1.20:
            return "xs_nc"
        elif cross_section["sections"][0]["width"] == 0.95:
            return "xs_no"
        else:
            raise err
    else:
        raise err


@partial(jax.jit, static_argnames=["cross_section"])
def _straight(
    *,
    wl: float = 1.55,
    length: float = 10.0,
    loss: float = 0.0,
    cross_section="xs_sc",
):
    print(cross_section)
    if _check_cross_section(cross_section) == "xs_sc":
        print("straight_sc")
        return straight_sc(wl=wl, length=length, loss=loss)
    elif _check_cross_section(cross_section) == "xs_so":
        print("straight_so")
        return straight_so(wl=wl, length=length, loss=loss)
    elif _check_cross_section(cross_section) == "xs_rc":
        print("straight_rc")
        return straight_rc(wl=wl, length=length, loss=loss)
    elif _check_cross_section(cross_section) == "xs_ro":
        print("straight_ro")
        return straight_ro(wl=wl, length=length, loss=loss)
    elif _check_cross_section(cross_section) == "xs_nc":
        print("straight_nc")
        return straight_nc(wl=wl, length=length, loss=loss)
    elif _check_cross_section(cross_section) == "xs_no":
        print("straight_no")
        return straight_no(wl=wl, length=length, loss=loss)
    else:
        raise ValueError(f"Invalid cross section: Got: {cross_section}")


_bend_euler = partial(bend, loss=0.03)
bend_sc = partial(bend, loss=0.03)
bend_so = partial(bend, loss=0.03)
bend_rc = partial(bend, loss=0.03)
bend_ro = partial(bend, loss=0.03)
bend_nc = partial(bend, loss=0.03)
bend_no = partial(bend, loss=0.03)

################
# Transitions
################

trans_sc_rc10 = _2port("o1", "o2")
trans_sc_rc20 = _2port("o1", "o2")
trans_sc_rc50 = _2port("o1", "o2")

################
# MMIs
################

mmi1x2_rc = coupler
mmi2x2_rc = coupler
mmi1x2_sc = coupler
mmi2x2_sc = coupler
mmi1x2_ro = coupler
mmi2x2_ro = coupler
mmi1x2_so = coupler
mmi2x2_so = coupler
mmi1x2_no = coupler
mmi2x2_no = coupler
mmi1x2_nc = coupler
mmi2x2_nc = coupler

##############################
# grating couplers Rectangular
##############################

_gco = partial(grating_coupler, loss=6, bandwidth=35 * nm, wl0=1.31)
_gcc = partial(grating_coupler, loss=6, bandwidth=35 * nm, wl0=1.55)
gc_rectangular_so = _gco
gc_rectangular_ro = _gco
gc_rectangular_no = _gco
gc_rectangular_sc = _gcc
gc_rectangular_rc = _gcc
gc_rectangular_nc = _gcc


################
# Crossings
################
@jax.jit
def _crossing(wl=1.5):
    wl = jnp.asarray(wl)
    one = jnp.ones_like(wl)
    return sax.reciprocal(
        {
            ("o1", "o3"): one,
            ("o2", "o4"): one,
        }
    )


crossing_so = _crossing
crossing_rc = _crossing
crossing_sc = _crossing


################
# Dummies
################
pad = _2port("o1", "o2")  # dummy model
heater = _2port("o1", "o2")  # dummy model

models = dict(
    _2port=_2port("o1", "o2"),
    _3port=_3port("o1", "o2", "o3"),
    _4port=_4port("o1", "o2", "o3", "o4"),
    straight=_straight,
    straight_sc=straight_sc,
    straight_so=straight_so,
    straight_rc=straight_rc,
    straight_ro=straight_ro,
    straight_nc=straight_nc,
    straight_no=straight_no,
    bend_euler=_bend_euler,
    bend_sc=bend_sc,
    bend_so=bend_so,
    bend_rc=bend_rc,
    bend_ro=bend_ro,
    bend_nc=bend_nc,
    bend_no=bend_no,
    trans_sc_rc10=trans_sc_rc10,
    trans_sc_rc20=trans_sc_rc20,
    trans_sc_rc50=trans_sc_rc50,
    mmi1x2_rc=mmi1x2_rc,
    mmi2x2_rc=mmi2x2_rc,
    mmi1x2_sc=mmi1x2_sc,
    mmi2x2_sc=mmi2x2_sc,
    mmi1x2_ro=mmi1x2_ro,
    mmi2x2_ro=mmi2x2_ro,
    mmi1x2_so=mmi1x2_so,
    mmi2x2_so=mmi2x2_so,
    mmi1x2_no=mmi1x2_no,
    mmi2x2_no=mmi2x2_no,
    mmi1x2_nc=mmi1x2_nc,
    mmi2x2_nc=mmi2x2_nc,
    gc_rectangular_so=gc_rectangular_so,
    gc_rectangular_ro=gc_rectangular_ro,
    gc_rectangular_no=gc_rectangular_no,
    gc_rectangular_sc=gc_rectangular_sc,
    gc_rectangular_rc=gc_rectangular_rc,
    gc_rectangular_nc=gc_rectangular_nc,
    crossing_so=crossing_so,
    crossing_rc=crossing_rc,
    crossing_sc=crossing_sc,
    pad=pad,
    heater=heater,
)


if __name__ == "__main__":
    print(coupler())
