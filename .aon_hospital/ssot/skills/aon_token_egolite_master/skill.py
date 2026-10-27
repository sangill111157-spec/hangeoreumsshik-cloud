#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aon_token_egolite_master skill entrypoint"""

import rgon_aon_token_egolite_master as master

def run(prompt=""):
    return master.route_token_egolite_intent(prompt)

if __name__ == "__main__":
    print(run("토큰 절약 및 에고라이트 번들링 검사"))
