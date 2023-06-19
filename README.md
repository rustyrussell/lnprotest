# lnprotest: framework to write Lightning protocol tests 

Before (lnprototest):

```
def has_one_feature(
    featurebits: List[int], event: Event, msg: Message, runner: "Runner"
) -> None:
    has_any = False
    for bit in featurebits:
        if has_bit(msg.fields["features"], bit):
            has_any = True

    if not has_any:
        raise EventError(event, "none of {} set: {}".format(featurebits, msg.to_str()))

def test_init_advertize_option_static_remotekey(
    runner: Runner, namespaceoverride: Any
) -> None:
    """TODO"""
    namespaceoverride(pyln.spec.bolt1.namespace)
    sequences = [
        Connect(connprivkey="03"),
        ExpectMsg("init"),
        Msg("init", globalfeatures="", features=""),
        # optionally disconnect that first one
        TryAll([], Disconnect()),
        Connect(connprivkey="02"),
        # BOLT-a12da24dd0102c170365124782b46d9710950ac1 #9:
        # | Bits  | Name                    | ... | Dependencies
        # ...
        # | 12/13 | `option_static_remotekey` |
        # ...
        # | 20/21 | `option_anchor_outputs` | ... | `option_static_remotekey` |
        # If you support `option_anchor_outputs`, you will
        # advertize option_static_remotekey.
        Sequence(
            [ExpectMsg("init", if_match=functools.partial(has_one_feature, [12, 13]))],
            enable=(runner.has_option("option_anchor_outputs") is not None),
        ),
    ]
    run_runner(runner, sequences)
```

But this is what I want it to look like:

```
def test_init_advertize_option_static_remotekey(runner: Runner):
    conn = runner.connect(connprivkey="03")
    assert type(conn.recv()) is pyln.proto.Init
    conn.send(pyln.proto.Init(globalfeatures="", features="")

    # optionally disconnect that first one
    if runner.choose([True, False]):
        conn.disconnect()
        conn = runner.connect(connprivkey="02")
        assert type(conn.recv()) is pyln.proto.Init
        conn.send(pyln.proto.Init(globalfeatures="", features="")

    # BOLT-a12da24dd0102c170365124782b46d9710950ac1 #9:
    # | Bits  | Name                    | ... | Dependencies
    # ...
    # | 12/13 | `option_static_remotekey` |
    # ...
    # | 20/21 | `option_anchor_outputs` | ... | `option_static_remotekey` |
    # If you support `option_anchor_outputs`, you will
    # advertize option_static_remotekey.
    initmsg = conn.recv()
    assert initmsg is pyln.proto.Init

    # If you support option_anchor_outputs you must offer it
    if runner.has_option("option_anchor_outputs"):
        assert initmsg.features.offers(20):

    # And if you offer it, you must offer static_remotekey
    if initmsg.features.offers(20):
        assert initmsg.features.offers(12)
```
