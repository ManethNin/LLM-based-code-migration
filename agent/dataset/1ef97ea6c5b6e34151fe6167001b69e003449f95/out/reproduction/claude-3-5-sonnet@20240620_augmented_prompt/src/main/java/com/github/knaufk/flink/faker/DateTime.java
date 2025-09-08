package com.github.knaufk.flink.faker;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.Date;
import java.util.concurrent.TimeUnit;
import net.datafaker.DateAndTime;
import net.datafaker.Faker;

public class DateTime extends DateAndTime {

  protected DateTime(Faker faker) {
    super(faker);
  }

  public Timestamp past(int atMost, TimeUnit unit) {
    return Timestamp.from(super.past(atMost, unit).toInstant());
  }

  public Timestamp past(int atMost, int minimum, TimeUnit unit) {
    return Timestamp.from(super.past(atMost, minimum, unit).toInstant());
  }

  public Timestamp future(int atMost, TimeUnit unit) {
    return Timestamp.from(super.future(atMost, unit).toInstant());
  }

  public Timestamp future(int atMost, int minimum, TimeUnit unit) {
    return Timestamp.from(super.future(atMost, minimum, unit).toInstant());
  }

  public Timestamp future(int atMost, TimeUnit unit, Date referenceDate) {
    return Timestamp.from(super.future(atMost, unit, referenceDate).toInstant());
  }

  public Timestamp past(int atMost, TimeUnit unit, Date referenceDate) {
    return Timestamp.from(super.past(atMost, unit, referenceDate).toInstant());
  }

  public Timestamp between(Date from, Date to) throws IllegalArgumentException {
    Timestamp fromTimestamp = new Timestamp(from.getTime());
    Timestamp toTimestamp = new Timestamp(to.getTime());
    return super.between(fromTimestamp, toTimestamp);
  }

  public Timestamp birthday() {
    return Timestamp.from(super.birthday().toInstant());
  }

  public Timestamp birthday(int minAge, int maxAge) {
    return Timestamp.from(super.birthday(minAge, maxAge).toInstant());
  }
}
