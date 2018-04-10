(define (domain robot-d)

  (:requirements
    :strips
    :typing
  )

  (:predicates
   (succ ?i1 ?i2)
   (at ?what ?x ?y)
   (in ?what ?where)
   (nexto ?what ?x ?y)
   (robot ?who)
   (wall ?what)
   (table ?what)
   (cloth ?what)
   (tray ?what)
   (seat ?what)
   (dishWash ?what)
   (washMach ?what)
   (closet ?what)
   (holding ?what)
   (clean ?what)
   (clear ?what)
  )
   
  (:action moveRight
    :parameters (?r ?x1 ?x2 ?y)
    :precondition (and
                    (robot ?r)
                    (succ ?x1 ?x2) 
                    (at ?r ?x1 ?y)
                    (forall (?z)
                      (not (at ?z ?x2 ?y))))
    :effect (and
              (at ?r ?x2 ?y)
              (not (at ?r ?x1 ?y)))
  )

  (:action moveLeft
    :parameters (?r ?x2 ?x1 ?y)
    :precondition (and
                    (robot ?r)
                    (succ ?x1 ?x2)
                    (at ?r ?x2 ?y)
                    (forall (?z)
                      (not (at ?z ?x1 ?y))))
    :effect (and
              (at ?r ?x1 ?y)
              (not (at ?r ?x2 ?y)))
  )

  (:action moveUp
    :parameters (?r ?x ?y1 ?y2)
    :precondition (and
                    (robot ?r)
                    (succ ?y1 ?y2)
                    (at ?r ?x ?y1)
                    (forall (?z)
                      (not (at ?z ?x ?y2))))
    :effect (and
              (at ?r ?x ?y2)
              (not (at ?r ?x ?y1)))
  )

  (:action moveDown
    :parameters (?r ?x ?y2 ?y1)
    :precondition (and
                    (robot ?r)
                    (succ ?y1 ?y2)
                    (at ?r ?x ?y2)
                    (forall (?z)
                      (not (at ?z ?x ?y1))))
    :effect (and
              (at ?r ?x ?y1)
              (not (at ?r ?x ?y2)))
  )

  (:action grab
    :parameters (?r ?what ?where)
    :precondition (and
                    (forall (?z)
                      (not (holding ?z)))
                    (exists (?x ?y)
                      (and
                        (robot ?r)
                        (at ?r ?x ?y)
                        (in ?what ?where)
                        (nexto ?where ?x ?y)
                        (or
                          (tray ?what)
                          (and
                            (cloth ?what)
                            (or
                              (washMach ?where)
                              (and
                                (table ?where)
                                (not (exists (?c)
                                  (and
                                    (tray ?c)
                                    (not (clear ?c))))))))))))
    :effect (and
              (holding ?what)
              (not (in ?what ?where))
              (when (tray ?what)
                (clear ?what)))
  )

  (:action put
    :parameters (?r ?what ?where)
    :precondition (and
                    (holding ?what)
                    (exists (?x ?y)
                      (and
                        (robot ?r)
                        (at ?r ?x ?y)
                        (nexto ?where ?x ?y)
                        (or
                          (and
                            (tray ?what)
                            (or
                              (dishWash ?where)
                              (and
                                (closet ?where)
                                (clean ?what))))
                          (and
                            (cloth ?what)
                            (or
                              (washMach ?where)
                              (table ?where)))))))
    :effect (and
              (in ?what ?where)
              (not (holding ?what)))
  )

  (:action wash
    :parameters (?r ?where)
    :precondition (and
                    (exists (?c)
                      (and
                        (in ?c ?where)
                        (not (clean ?c))))
                    (or
                      (dishWash ?where)
                      (washMach ?where))
                    (exists (?x ?y)
                      (and
                        (robot ?r)
                        (at ?r ?x ?y)
                        (nexto ?where ?x ?y))))
    :effect (forall (?z)
              (when (in ?z ?where)
                (clean ?z)))
  )

)
