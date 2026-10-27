#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aon_vibe3d_movie_director skill entrypoint"""

import rgon_aon_vibe3d_director as director

def run(prompt=""):
    return director.route_vibe3d_intent(prompt)

if __name__ == "__main__":
    print(run("해상이와 아온이 시네마틱 3D 세트장"))
