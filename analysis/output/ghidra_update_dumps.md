# Update Function Instruction Dumps

## `09047c9a`

- Name: `UPD_09047c9a`
- Entry: `09047c9a`

```text
09047c9a: moveq #-0x2e,D7
09047c9c: bchg.l D5,D2
09047c9e: btst.l D4,D0
09047ca0: sub.l -(A5),D2
09047ca2: btst.l D4,D0
09047ca4: bcc.b 0x09047c82
09047ca6: moveq #-0x30,D6
09047ca8: abcd D2b,D6b
09047caa: move.l -(A2),D4
09047cac: movep.w D0w,(-0x725b,A1)
09047cb0: btst.l D4,D0
09047cb2: moveq #-0x2e,D5
09047cb4: bchg.l D5,D2
09047cb6: sgt -(A4)
09047cb8: or.l -(A5),D4
09047cba: btst.l D4,D0
```

## `0904f61c`

- Name: `UPD_0904f61c`
- Entry: `0904f61c`

```text
0904f61c: btst.l D4,D0
0904f61e: sub.l -(A0),D2
0904f620: btst.l D4,D0
0904f622: sub.l D1,-(A0)
```

## `0908925e`

- Name: `UPD_0908925e`
- Entry: `0908925e`

```text
0908925e: btst.l D4,D0
09089260: msac.w D0u,D4w<<1,-(A0),D7,ACC1
09089264: sge (A4)
09089266: slt (A5)
09089268: slt (A2)
0908926a: bchg.l D5,D2
0908926c: btst.l D4,D0
0908926e: slt (A5)
09089270: slt (A4)
09089272: sgt (A6)
09089274: sgt (A2)
09089276: addq.b #0x2,(SP)+
09089278: chk.l (SP)+,D1
0908927a: bchg.l D5,D2
0908927c: bcs.b 0x0908929d
```

## `09000482`

- Name: `UPD_09000482`
- Entry: `09000482`

```text
09000482: move.b A1b,([0x9007ea0,-,A1w*0x8],0x1e090fe)
0900048e: ori.b #0x1,D0b
09000492: ori.l #-0x7cfee000,-(A4)
09000498: cmpi.b #0x0,D3b
0900049c: neg.b D4b
0900049e: move.l D0,D0
090004a0: btst.l D2,D5
090004a2: move.l D0,D0
090004a4: sbcd D6b,D2b
090004a6: move.l D0,D0
090004a8: mvs.b: (A1),D7
090004aa: move.l D0,D0
090004ac: movep.w (0x2000,A1),D0w
090004b0: movep.w (0x2000,A2),D0w
```

## `090004ea`

- Name: `UPD_090004ea`
- Entry: `090004ea`

```text
090004ea: moveq #-0x41,D2
090004ec: btst.l D4,D0
090004ee: bhi.b 0x090004af
```

## `09010412`

- Name: `UPD_09010412`
- Entry: `09010412`

```text
09010412: btst.l D4,D0
09010414: moveq #-0x41,D7
09010416: btst.l D4,D0
```

## `09010432`

- Name: `UPD_09010432`
- Entry: `09010432`

```text
09010432: btst.l D4,D0
09010434: moveq #-0x41,D7
09010436: btst.l D4,D0
```

## `0904644e`

- Name: `UPD_0904644e`
- Entry: `0904644e`

```text
0904644e: btst.l D4,D0
09046450: divu.w (A4),D0
09046452: divs.w (A5),D1
09046454: divs.w (A2),D1
09046456: bchg.l D5,D2
09046458: btst.l D4,D0
0904645a: moveq #-0x2c,D7
0904645c: bgt.b 0x09046443
```

