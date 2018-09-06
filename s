func numJewelsInStones(J string, S string) int {

    d := make(map[rune]int)

    for _, v  := range S {

        if _, ok := d[v]; ok {

            d[v] += 1

        } else {

            d[v] = 1

        }

    }

    

    rst := 0

    for _, v := range J {

        if _, ok := d[v]; ok {

            rst += d[v]

        }

    }

    return rst

}
